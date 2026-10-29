"""Best-agent replay (#28, spec sections 2, 5 and 11): a recorded Controller log
fed into one Attempt in the main process, never by re-running a genome.

The run replayed here is recorded by the real Trainer and RunRecorder with the
random-buttons double, and stopped early, after its second generation of three.
"""

import os
import subprocess
import sys
import types
from datetime import datetime
from pathlib import Path

import numpy as np
import pygame
import pytest

import mario
from mario.level.static_level import StaticLevel
from mario.modes.play_session import PlaySession
from mario.modes.replay_mode import ReplayMode
from mario.modes.replay_session import ReplaySession
from mario.recording.recorded_run import RecordedRun
from mario.recording.run_recorder import RunRecorder
from mario.simulation.attempt import Attempt
from mario.simulation.attempt_result import EndReason
from mario.training.agent_worker_pool import AgentWorkerPool
from mario.training.algorithm_factory import AlgorithmFactory
from mario.training.brain_chunk_controller_source import BrainChunkControllerSourceFactory
from mario.training.generation_recorder import GenerationRecorder
from mario.training.run_config import RunSettings
from mario.training.trainer import GenerationListener, GenerationReport, Trainer
from mario.view.viewer import Viewer
from tests.game.helpers import CASTLE_STOPPER_X_PIXELS, HOLD_NOTHING, PILOT_ENEMY_LOOK_AHEAD_PIXELS
from tests.game.mario_with_a_frame_budget import FRAMES_SHOWN_PREFIX, NEUROEVOLUTION_IMPORTED_PREFIX
from tests.game.random_buttons_algorithm import create_random_buttons_algorithm
from tests.game.scripted_pilot import ScriptedPilot
from tests.game.scripted_window import F1_PRESSED, NOTHING_PRESSED, ScriptedWindow, shows_the_sprite_view

REPO_ROOT = Path(mario.__file__).parent.parent
FRAME_BUDGET_SCRIPT = Path(__file__).parent / "mario_with_a_frame_budget.py"
SEED = 28
PLANNED_GENERATIONS = 3
GENERATIONS_BEFORE_THE_STOP = 2
POPULATION_SIZE = 6
WORKER_COUNT = 2
RUN_NAME = "stopped"
STARTED_AT = datetime(2026, 10, 28, 9, 30)


class StopAfter(GenerationListener):
    """Stops the run as Ctrl+C would, once the given generation is recorded."""
    def __init__(self, last_generation: int):
        self._last_generation = last_generation

    def generation_finished(self, report: GenerationReport) -> None:
        if report.generation == self._last_generation:
            raise KeyboardInterrupt


@pytest.fixture(scope="module")
def stopped_run(tmp_path_factory) -> Path:
    """The folder of a 3-generation run stopped after its second generation."""
    folder = tmp_path_factory.mktemp("stopped")
    config_path = folder / "config.toml"
    config_path.write_text(f'[run]\nname = "{RUN_NAME}"\n')
    recorder = RunRecorder.start(folder / "runs", RUN_NAME, config_path, STARTED_AT)
    run_settings = RunSettings(name=RUN_NAME, seed=SEED, generations=PLANNED_GENERATIONS,
                               population_size=POPULATION_SIZE)
    algorithm_factory = AlgorithmFactory(create_random_buttons_algorithm, {})
    with (pytest.raises(KeyboardInterrupt),
          AgentWorkerPool(BrainChunkControllerSourceFactory(algorithm_factory), WORKER_COUNT) as worker_pool):
        Trainer(algorithm_factory.create(), worker_pool, run_settings,
                [GenerationRecorder(recorder), StopAfter(GENERATIONS_BEFORE_THE_STOP)]).run()
    return recorder.run_folder_path


@pytest.fixture
def fonts():
    pygame.font.init()
    yield
    pygame.font.quit()


def best_agent_session(run_folder: Path, generation: int, level: StaticLevel) -> ReplaySession:
    recorded_run = RecordedRun(run_folder)
    best_agent = recorded_run.best_agent(generation)
    return ReplaySession(recorded_run.controller_log(generation, best_agent.agent_index), level)


def replay_to_the_end(session: ReplaySession) -> None:
    while not session.is_finished:
        session.step()


def pilots_controller_log(level: StaticLevel) -> np.ndarray:
    """The Controller log of a training attempt (stall rule on) in which the pilot reaches the flag."""
    attempt = Attempt(level, ends_on_stall=True)
    pilot = ScriptedPilot(PILOT_ENEMY_LOOK_AHEAD_PIXELS)
    controller_log = bytearray()
    while not attempt.is_over:
        buttons = pilot.next_buttons(attempt)
        attempt.step(buttons)
        controller_log.append(buttons)
    assert attempt.end_reason is EndReason.REACHED_FLAG
    return np.frombuffer(bytes(controller_log), dtype=np.uint8)


def test_a_run_stopped_early_replays_from_its_last_recorded_generation(stopped_run):
    assert RecordedRun(stopped_run).last_generation() == GENERATIONS_BEFORE_THE_STOP


@pytest.mark.parametrize("generation", range(1, GENERATIONS_BEFORE_THE_STOP + 1))
def test_replaying_the_best_agent_ends_as_its_recorded_attempt_ended(stopped_run, world_1_1, generation):
    best_agent = RecordedRun(stopped_run).best_agent(generation)
    session = best_agent_session(stopped_run, generation, world_1_1)
    replay_to_the_end(session)
    result = session.attempt.result()
    assert (result.end_reason, result.furthest_x, result.ticks_elapsed, result.final_score,
            result.coins_collected) == (best_agent.end_reason, best_agent.furthest_x, best_agent.ticks_elapsed,
                                        best_agent.final_score, best_agent.coins_collected)


def test_the_replay_holds_still_once_the_recorded_attempt_has_ended(stopped_run, world_1_1):
    session = best_agent_session(stopped_run, GENERATIONS_BEFORE_THE_STOP, world_1_1)
    replay_to_the_end(session)
    last_snapshot = session.snapshot()
    session.step()
    assert session.is_finished and session.snapshot() == last_snapshot


def test_a_replay_that_reached_the_flag_plays_out_the_end_of_the_level_as_play_mode_does(world_1_1):
    """Play mode's end of the level is the reference (tests/game/test_end_of_level.py checks it)."""
    controller_log = pilots_controller_log(world_1_1)
    replay = ReplaySession(controller_log, world_1_1)
    play = PlaySession(world_1_1)
    replay_snapshots, play_snapshots = [], []
    played_attempt = play.attempt
    for buttons in controller_log.tolist():
        replay.step()
        play.step(buttons)
    while not played_attempt.end_of_level.is_over:  # then play mode starts a new game
        replay_snapshots.append(replay.snapshot())
        play_snapshots.append(play.snapshot())
        assert not replay.is_finished
        replay.step()
        play.step(buttons)
    assert replay_snapshots == play_snapshots
    replay_to_the_end(replay)
    last_snapshot = replay.snapshot()
    assert replay.attempt.end_of_level.is_over
    assert last_snapshot.mario.x_pixels + last_snapshot.mario.width_pixels == CASTLE_STOPPER_X_PIXELS
    assert (last_snapshot.hud.score, last_snapshot.hud.time_left) == (replay.attempt.result().final_score, 0)


def test_replay_starts_in_the_sprite_view_and_f1_switches_to_the_debug_view_and_back(
        fonts, stopped_run, world_1_1, tmp_path):
    window = ScriptedWindow([NOTHING_PRESSED, F1_PRESSED, NOTHING_PRESSED, F1_PRESSED])
    ReplayMode(best_agent_session(stopped_run, GENERATIONS_BEFORE_THE_STOP, world_1_1),
               Viewer.with_both_views(window, tmp_path)).run()
    assert [shows_the_sprite_view(frame) for frame in window.frames_shown] == [True, False, False, True]
    assert window.is_closed


def test_the_replay_mode_shows_the_whole_recorded_attempt_until_the_viewer_quits(
        fonts, stopped_run, world_1_1, tmp_path, monkeypatch):
    """With an empty neuroevolution package in place of the user's, and frames left over at the end."""
    monkeypatch.setitem(sys.modules, "neuroevolution", types.ModuleType("neuroevolution"))
    best_agent = RecordedRun(stopped_run).best_agent(GENERATIONS_BEFORE_THE_STOP)
    frames_after_the_end = 3
    window = ScriptedWindow([NOTHING_PRESSED] * (best_agent.ticks_elapsed + frames_after_the_end))
    session = best_agent_session(stopped_run, GENERATIONS_BEFORE_THE_STOP, world_1_1)
    ReplayMode(session, Viewer.with_both_views(window, tmp_path)).run()
    assert len(window.frames_shown) == best_agent.ticks_elapsed + frames_after_the_end
    assert (session.attempt.end_reason, session.attempt.furthest_x) == (best_agent.end_reason, best_agent.furthest_x)
    assert window.is_closed


def test_without_a_generation_the_replay_mode_replays_the_last_recorded_one(
        fonts, stopped_run, tmp_path, monkeypatch, capsys):
    monkeypatch.setattr("mario.modes.replay_mode.Window", lambda: ScriptedWindow([]))
    best_agent = RecordedRun(stopped_run).best_agent(GENERATIONS_BEFORE_THE_STOP)
    ReplayMode.of_best_agent(stopped_run, None, tmp_path).run()
    assert capsys.readouterr().out.startswith(
        f"Replaying generation {GENERATIONS_BEFORE_THE_STOP}, best agent {best_agent.agent_index} ")


def replay_command(*arguments: str) -> subprocess.CompletedProcess:
    """`py -m mario replay ...`, run from the repo root."""
    return subprocess.run([sys.executable, "-m", "mario", "replay", *arguments], cwd=REPO_ROOT,
                          env={**os.environ, "SDL_VIDEODRIVER": "dummy"}, capture_output=True, text=True,
                          timeout=60)


def test_replay_of_a_generation_not_recorded_exits_with_a_clear_message(stopped_run):
    finished = replay_command(str(stopped_run), "--generation", str(PLANNED_GENERATIONS), "--best")
    assert finished.returncode != 0
    assert f"generation {PLANNED_GENERATIONS} isn't recorded" in finished.stderr
    assert "Traceback" not in finished.stderr


def test_replay_of_a_folder_that_is_not_a_run_folder_exits_with_a_clear_message(tmp_path):
    finished = replay_command(str(tmp_path), "--best")
    assert finished.returncode != 0
    assert "not a run folder" in finished.stderr and "Traceback" not in finished.stderr


def one_stalled_agent_run(runs_root: Path, level: StaticLevel) -> tuple[Path, int]:
    """A one-generation, one-agent run folder whose agent pressed nothing until the stall rule ended
    its attempt, written by the real RunRecorder; and that attempt's length in ticks."""
    config_path = runs_root / "config.toml"
    config_path.write_text(f'[run]\nname = "{RUN_NAME}"\n')
    recorder = RunRecorder.start(runs_root, RUN_NAME, config_path, STARTED_AT)
    attempt = Attempt(level, ends_on_stall=True)
    while not attempt.is_over:
        attempt.step(HOLD_NOTHING)
    attempt_result = attempt.result()
    controller_log = np.full(attempt_result.ticks_elapsed, HOLD_NOTHING, dtype=np.uint8)
    recorder.record_generation(1, [attempt_result], [controller_log], np.array([1.0]), [np.zeros(1)], seconds=0.0)
    return recorder.run_folder_path, attempt_result.ticks_elapsed


def test_py_m_mario_replay_best_runs_to_the_viewer_quitting_with_an_empty_neuroevolution_package(
        world_1_1, tmp_path):
    """From a folder whose empty neuroevolution package shadows the user's, as while it is unwritten."""
    working_folder = tmp_path / "working"
    (working_folder / "neuroevolution").mkdir(parents=True)
    (working_folder / "neuroevolution" / "__init__.py").write_text("")
    run_folder, ticks_elapsed = one_stalled_agent_run(tmp_path, world_1_1)
    frame_budget = ticks_elapsed + 3  # the whole attempt, then its last frame held
    finished = subprocess.run(
        [sys.executable, str(FRAME_BUDGET_SCRIPT), str(frame_budget), "replay", str(run_folder), "--best"],
        cwd=working_folder, capture_output=True, text=True, timeout=60,
        env={**os.environ, "SDL_VIDEODRIVER": "dummy",
             "PYTHONPATH": os.pathsep.join([str(working_folder), str(REPO_ROOT)])})
    assert finished.returncode == 0, finished.stderr
    assert "Replaying generation 1, best agent 0 " in finished.stdout
    assert f"{FRAMES_SHOWN_PREFIX}{frame_budget}" in finished.stdout
    assert f"{NEUROEVOLUTION_IMPORTED_PREFIX}False" in finished.stdout
