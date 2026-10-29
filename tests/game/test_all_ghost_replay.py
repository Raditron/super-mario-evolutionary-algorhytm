"""All-ghost replay (#30, spec sections 2, 8 and 11): every agent of a recorded generation
replayed from its Controller log through watch-live's worker + snapshot pipeline,
never by re-running a genome, and never importing the user's neuroevolution package.

The run replayed here is recorded by the real Trainer and RunRecorder with the
random-buttons double.
"""

import os
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import numpy as np
import pygame
import pytest

import mario
from mario.level.static_level import StaticLevel
from mario.modes.all_ghost_replay_mode import AllGhostReplayMode
from mario.modes.watch_live import WatchLive
from mario.recording.recorded_run import RecordedRun
from mario.recording.run_recorder import RunRecorder
from mario.simulation.attempt_result import AttemptResult, EndReason
from mario.snapshots.world_snapshot import GenerationProgress, WorldSnapshot
from mario.training.agent_worker_pool import AgentWorkerPool
from mario.training.algorithm_factory import AlgorithmFactory
from mario.training.chunk_player import PlayedAttempt
from mario.training.brain_chunk_controller_source import BrainChunkControllerSourceFactory
from mario.training.controller_log_chunk_controller_source import ControllerLogChunkControllerSourceFactory
from mario.training.generation_recorder import GenerationRecorder
from mario.training.run_config import RunSettings
from mario.training.trainer import Trainer
from mario.view.viewer import Viewer
from mario.view.window import WindowEvents
from tests.game.helpers import PILOT_ENEMY_LOOK_AHEAD_PIXELS
from tests.game.mario_with_a_frame_budget import FRAMES_SHOWN_PREFIX, NEUROEVOLUTION_IMPORTED_PREFIX
from tests.game.random_buttons_algorithm import create_random_buttons_algorithm
from tests.game.scripted_pilot import pilots_training_attempt
from tests.game.scripted_window import CLOSED, NOTHING_PRESSED, ScriptedWindow

REPO_ROOT = Path(mario.__file__).parent.parent
FRAME_BUDGET_SCRIPT = Path(__file__).parent / "mario_with_a_frame_budget.py"
SEED = 30
GENERATIONS = 2
POPULATION_SIZE = 10
WORKER_COUNT = 2
RUN_NAME = "replayed"
STARTED_AT = datetime(2026, 10, 29, 9, 0)
# Frames the viewer keeps showing the finished generation before it quits.
FRAMES_HELD_AFTER_THE_END = 30
# Frames shown before the viewer quits part-way through the generation.
FRAMES_BEFORE_QUITTING_EARLY = 5
# Quit part-way, the replay is over well within this, though the generation's
# attempts would take longer: each lasts at least the stall limit's 3 seconds.
SECONDS_TO_STOP = 2.0
# Few enough frames for `py -m mario replay` to be quit part-way through its generation.
FRAME_BUDGET = 20
IMPORTED_MARKER_FILE_NAME = "imported"
# A neuroevolution package that leaves a file beside itself when any process imports it.
MARKING_PACKAGE = f"""from pathlib import Path
Path(__file__).with_name({IMPORTED_MARKER_FILE_NAME!r}).touch()
"""


@dataclass
class EndlessWindow(ScriptedWindow):
    """A window nobody closes; it counts the frames shown rather than keeping them,
    since nothing paces the watch loop's frames here."""
    frame_count: int = 0

    def poll_events(self) -> WindowEvents:
        return NOTHING_PRESSED

    def present(self) -> None:
        self.frame_count += 1


@dataclass
class QuitsOnItsOwnWindow(EndlessWindow):
    """Quits once it has shown the given number of frames, noting when."""
    frames_before_quitting: int = FRAMES_BEFORE_QUITTING_EARLY
    quit_at: float | None = None

    def poll_events(self) -> WindowEvents:
        if self.frame_count < self.frames_before_quitting:
            return NOTHING_PRESSED
        if self.quit_at is None:
            self.quit_at = time.perf_counter()
        return CLOSED


class WatchingViewer:
    """The real Viewer, noting the HUD's generation line and the ghosts of every
    snapshot it shows; it quits once it has shown the finished generation for a while."""

    def __init__(self, viewer: Viewer):
        self._viewer = viewer
        self.generation_lines: list[GenerationProgress] = []
        self.ghost_counts: list[int] = []
        self.frames_shown_after_the_end = 0

    def handle_events(self) -> bool:
        return self.frames_shown_after_the_end > FRAMES_HELD_AFTER_THE_END or self._viewer.handle_events()

    def show(self, snapshot: WorldSnapshot) -> None:
        self.generation_lines.append(snapshot.generation_progress)
        self.ghost_counts.append(len(snapshot.ghosts))
        self._note_a_frame_shown()
        self._viewer.show(snapshot)

    def show_again(self) -> None:
        self._note_a_frame_shown()
        self._viewer.show_again()

    def close(self) -> None:
        self._viewer.close()

    def _note_a_frame_shown(self) -> None:
        if self.generation_lines and self.generation_lines[-1].alive == 0:
            self.frames_shown_after_the_end += 1


@pytest.fixture
def fonts():
    """The renderers need pygame's fonts, which the real Window initialises."""
    pygame.font.init()
    yield
    pygame.font.quit()


@pytest.fixture(scope="module")
def recorded_run_folder(tmp_path_factory) -> Path:
    """The folder of a finished 2-generation run of 10 agents."""
    folder = tmp_path_factory.mktemp("recorded")
    config_path = folder / "config.toml"
    config_path.write_text(f'[run]\nname = "{RUN_NAME}"\n')
    recorder = RunRecorder.start(folder / "runs", RUN_NAME, config_path, STARTED_AT)
    run_settings = RunSettings(name=RUN_NAME, seed=SEED, generations=GENERATIONS, population_size=POPULATION_SIZE)
    algorithm_factory = AlgorithmFactory(create_random_buttons_algorithm, {})
    with AgentWorkerPool(BrainChunkControllerSourceFactory(algorithm_factory), WORKER_COUNT) as worker_pool:
        Trainer(algorithm_factory.create(), worker_pool, run_settings, [GenerationRecorder(recorder)]).run()
    return recorder.run_folder_path


@pytest.fixture(scope="module")
def pilots_attempt() -> tuple[np.ndarray, AttemptResult]:
    """The Controller log and result of a training attempt that reaches the flag."""
    return pilots_training_attempt(StaticLevel.load_world_1_1(), PILOT_ENEMY_LOOK_AHEAD_PIXELS)


def results_rows_of(recorded_run: RecordedRun, generation: int):
    """The generation's rows of results.csv, in agent order."""
    return sorted((row for row in recorded_run.results_rows() if row.generation == generation),
                  key=lambda row: row.agent_index)


def endings_of(played_attempts: list[PlayedAttempt]) -> list[tuple[EndReason, int, int]]:
    return [(played.attempt_result.end_reason, played.attempt_result.furthest_x, played.attempt_result.ticks_elapsed)
            for played in played_attempts]


def recorded_endings(recorded_run: RecordedRun, generation: int) -> list[tuple[EndReason, int, int]]:
    return [(row.end_reason, row.furthest_x, row.ticks_elapsed) for row in results_rows_of(recorded_run, generation)]


@pytest.mark.parametrize("generation", range(1, GENERATIONS + 1))
def test_every_agent_replayed_from_its_controller_log_ends_as_results_csv_says_even_one_that_reached_the_flag(
        recorded_run_folder, pilots_attempt, generation):
    """The pilot's attempt joins the generation's recorded ones as its last agent, so one reaches the flag."""
    recorded_run = RecordedRun(recorded_run_folder)
    pilots_controller_log, pilots_result = pilots_attempt
    with AgentWorkerPool(ControllerLogChunkControllerSourceFactory(), WORKER_COUNT) as worker_pool:
        replayed_attempts = worker_pool.play(recorded_run.controller_logs(generation) + [pilots_controller_log],
                                             generation)
    assert len(results_rows_of(recorded_run, generation)) == POPULATION_SIZE
    assert endings_of(replayed_attempts) == recorded_endings(recorded_run, generation) + [
        (pilots_result.end_reason, pilots_result.furthest_x, pilots_result.ticks_elapsed)]
    assert replayed_attempts[-1].attempt_result.end_reason is EndReason.REACHED_FLAG


def test_the_replay_mode_plays_every_agent_of_the_generation_through_the_watched_pool_as_results_csv_says(
        fonts, recorded_run_folder, monkeypatch, tmp_path):
    """End to end through AllGhostReplayMode, its watched worker pool, snapshots and WatchLive; the
    WatchLive here lets the generation go once played, so the pool hands back what it played."""
    played_attempts: list[PlayedAttempt] = []

    class PlayedAttemptsKeepingWorkerPool(AgentWorkerPool):
        def play(self, agent_controls, generation):
            played_now = super().play(agent_controls, generation)
            played_attempts.extend(played_now)
            return played_now

    monkeypatch.setattr("mario.modes.all_ghost_replay_mode.AgentWorkerPool", PlayedAttemptsKeepingWorkerPool)
    recorded_run = RecordedRun(recorded_run_folder)
    window = EndlessWindow([])
    AllGhostReplayMode(1, recorded_run.controller_logs(1),
                       WatchLive(lambda: Viewer.with_both_views(window, tmp_path))).run()
    assert endings_of(played_attempts) == recorded_endings(recorded_run, 1)
    assert window.frame_count > 0 and window.is_closed


def test_the_replay_shows_the_whole_generation_with_ghosts_and_the_hud_line_then_holds_it_until_the_viewer_quits(
        fonts, recorded_run_folder, tmp_path):
    generation = GENERATIONS
    recorded_run = RecordedRun(recorded_run_folder)
    reached_flag_count = sum(row.end_reason is EndReason.REACHED_FLAG
                             for row in results_rows_of(recorded_run, generation))
    window = EndlessWindow([])
    viewer = WatchingViewer(Viewer.with_both_views(window, tmp_path))
    AllGhostReplayMode(generation, recorded_run.controller_logs(generation),
                       WatchLive(lambda: viewer, keeps_showing_once_played=True)).run()
    first_line, last_line = viewer.generation_lines[0], viewer.generation_lines[-1]
    assert (first_line.generation, first_line.population_size) == (generation, POPULATION_SIZE)
    assert first_line.alive > 0 and any(viewer.ghost_counts)
    assert last_line == GenerationProgress(generation, 0, POPULATION_SIZE, reached_flag_count)
    assert viewer.frames_shown_after_the_end > FRAMES_HELD_AFTER_THE_END
    assert window.is_closed


def test_quitting_part_way_through_stops_the_replay_at_once(fonts, recorded_run_folder, tmp_path):
    recorded_run = RecordedRun(recorded_run_folder)
    window = QuitsOnItsOwnWindow([])
    AllGhostReplayMode(1, recorded_run.controller_logs(1),
                       WatchLive(lambda: Viewer.with_both_views(window, tmp_path),
                                 keeps_showing_once_played=True)).run()
    assert time.perf_counter() - window.quit_at < SECONDS_TO_STOP  # the workers are stopped, not waited for
    assert window.is_closed


def test_without_a_generation_the_replay_replays_every_agent_of_the_last_recorded_one(
        fonts, recorded_run_folder, monkeypatch, tmp_path, capsys):
    monkeypatch.setattr("mario.modes.watch_live.Window", lambda: QuitsOnItsOwnWindow([]))
    AllGhostReplayMode.of_generation(recorded_run_folder, None, tmp_path).run()
    assert capsys.readouterr().out.startswith(f"Replaying generation {GENERATIONS}: all {POPULATION_SIZE} agents")


def replay_command_in(folder: Path, *arguments: str) -> subprocess.CompletedProcess:
    """`py -m mario replay ...` in the folder, beside a neuroevolution package that marks being imported,
    with the window closed after the frame budget."""
    (folder / "neuroevolution").mkdir()
    (folder / "neuroevolution" / "__init__.py").write_text(MARKING_PACKAGE)
    return subprocess.run(
        [sys.executable, str(FRAME_BUDGET_SCRIPT), str(FRAME_BUDGET), "replay", *arguments],
        cwd=folder, capture_output=True, text=True, timeout=120,
        env={**os.environ, "SDL_VIDEODRIVER": "dummy", "PYTHONPATH": os.pathsep.join([str(folder), str(REPO_ROOT)])})


def test_py_m_mario_replay_of_a_generation_without_best_replays_it_and_quits_cleanly_never_importing_neuroevolution(
        recorded_run_folder, tmp_path):
    """Neither the main process nor any worker imports the user's package."""
    finished = replay_command_in(tmp_path, str(recorded_run_folder), "--generation", "1")
    assert finished.returncode == 0, finished.stderr
    assert "Traceback" not in finished.stderr
    assert f"Replaying generation 1: all {POPULATION_SIZE} agents" in finished.stdout
    assert f"{FRAMES_SHOWN_PREFIX}{FRAME_BUDGET}" in finished.stdout
    assert f"{NEUROEVOLUTION_IMPORTED_PREFIX}False" in finished.stdout
    assert not (tmp_path / "neuroevolution" / IMPORTED_MARKER_FILE_NAME).exists()


def test_py_m_mario_replay_of_a_generation_not_recorded_exits_with_a_clear_message(recorded_run_folder, tmp_path):
    finished = replay_command_in(tmp_path, str(recorded_run_folder), "--generation", str(GENERATIONS + 1))
    assert finished.returncode != 0
    assert f"generation {GENERATIONS + 1} isn't recorded" in finished.stderr
    assert "Traceback" not in finished.stderr
