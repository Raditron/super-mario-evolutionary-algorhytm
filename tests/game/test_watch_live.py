"""Watch-live through the real worker pool (#29, spec sections 8, 9 and 11), driven by the random-buttons double.

Watched, the workers play every chunk at once at the game's own speed and
publish snapshots, while the main process shows them; training's results stay
exactly what a headless run gives.
"""

import time
from collections.abc import Callable
from datetime import datetime

import numpy as np
import pytest

from mario.constants.snapshots import WATCHED_TICKS_PER_SECOND
from mario.recording.recorded_run import RecordedRun
from mario.recording.run_recorder import RunRecorder
from mario.snapshots.snapshot_channel import SnapshotChannel
from mario.snapshots.world_snapshot import WorldSnapshot
from mario.training.agent_worker_pool import AgentWorkerPool
from mario.training.algorithm_factory import AlgorithmFactory
from mario.training.chunk_player import ChunkPlayer
from mario.training.generation_recorder import GenerationRecorder
from mario.training.play_watcher import PlayWatcher, ViewerClosed
from mario.training.run_config import RunSettings
from mario.training.trainer import GenerationListener, GenerationReport, Trainer
from mario.view.followed_agent_camera import FollowedAgentCamera
from tests.game.random_buttons_algorithm import RandomButtonsAlgorithm, create_random_buttons_algorithm

SEED = 29
GENERATIONS = 2
POPULATION_SIZE = 12
WORKER_COUNT = 2
# How often the stand-in window looks at the snapshots, as the real one draws.
LOOKS_PER_SECOND = 60
RUN_NAME = "watched"
STARTED_AT = datetime(2026, 10, 28, 12, 0)


class GenerationCollector(GenerationListener):
    def __init__(self):
        self.reports: list[GenerationReport] = []

    def generation_finished(self, report: GenerationReport) -> None:
        self.reports.append(report)


class LookingWatcher(PlayWatcher):
    """Stands in for the window: looks at the snapshots through the camera while the
    generation plays, keeping what it would have drawn. Given a generation to
    close in, it closes once it has seen that generation's first snapshot."""

    def __init__(self, closes_in_generation: int | None = None):
        self.shown: list[WorldSnapshot] = []
        self._closes_in_generation = closes_in_generation

    def watch_until_played(self, generation: int, population_size: int, channel: SnapshotChannel,
                           is_played: Callable[[], bool]) -> None:
        camera = FollowedAgentCamera()
        while not is_played():
            snapshot = camera.snapshot(generation, population_size, channel.read_all())
            if snapshot is not None:
                self.shown.append(snapshot)
                if generation == self._closes_in_generation:
                    raise ViewerClosed
            time.sleep(1 / LOOKS_PER_SECOND)


def train(play_watcher: PlayWatcher | None,
          extra_listeners: tuple[GenerationListener, ...] = ()) -> list[GenerationReport]:
    collector = GenerationCollector()
    run_settings = RunSettings(name=RUN_NAME, seed=SEED, generations=GENERATIONS, population_size=POPULATION_SIZE)
    algorithm_factory = AlgorithmFactory(create_random_buttons_algorithm, {})
    with AgentWorkerPool(algorithm_factory, WORKER_COUNT, play_watcher) as worker_pool:
        Trainer(algorithm_factory.create(), worker_pool, run_settings, [*extra_listeners, collector]).run()
    return collector.reports


@pytest.fixture(scope="module")
def watched_run() -> tuple[list[GenerationReport], LookingWatcher]:
    watcher = LookingWatcher()
    return train(watcher), watcher


def test_results_are_identical_with_and_without_watching_for_the_same_seed(watched_run):
    watched_reports, _ = watched_run
    headless_reports = train(None)
    for watched, headless in zip(watched_reports, headless_reports, strict=True):
        assert [played.attempt_result for played in watched.played_attempts] == [
            played.attempt_result for played in headless.played_attempts]
        assert [played.controller_log.tolist() for played in watched.played_attempts] == [
            played.controller_log.tolist() for played in headless.played_attempts]
        assert watched.fitnesses.tolist() == headless.fitnesses.tolist()
        assert [genome.tolist() for genome in watched.genomes] == [genome.tolist() for genome in headless.genomes]


def test_a_watched_generation_plays_at_the_games_own_speed_with_every_chunk_at_once(watched_run):
    """Its longest attempt sets its length: the chunks don't wait for one another."""
    watched_reports, _ = watched_run
    for report in watched_reports:
        longest_attempt_ticks = max(played.attempt_result.ticks_elapsed for played in report.played_attempts)
        assert report.seconds >= longest_attempt_ticks / WATCHED_TICKS_PER_SECOND
        assert report.seconds < 2 * longest_attempt_ticks / WATCHED_TICKS_PER_SECOND


def test_the_window_is_shown_each_generation_with_the_followed_agent_ghosts_and_the_hud_line(watched_run):
    watched_reports, watcher = watched_run
    for report in watched_reports:
        shown = [snapshot for snapshot in watcher.shown if snapshot.generation_progress.generation == report.generation]
        assert shown, f"nothing shown of generation {report.generation}"
        assert any(snapshot.ghosts for snapshot in shown)
        assert all(snapshot.observation is not None for snapshot in shown)
        first, last = shown[0].generation_progress, shown[-1].generation_progress
        assert first.population_size == POPULATION_SIZE and first.alive > last.alive
        # the followed agent is the rightmost of those drawn
        for snapshot in shown:
            assert all(ghost.mario.x_pixels <= snapshot.mario.x_pixels for ghost in snapshot.ghosts)
            assert len(snapshot.ghosts) <= max(snapshot.generation_progress.alive - 1, 0)


def test_closing_the_window_stops_the_run_leaving_only_complete_generations(tmp_path):
    config_path = tmp_path / "config.toml"
    config_path.write_text(f'[run]\nname = "{RUN_NAME}"\n')
    recorder = RunRecorder.start(tmp_path / "runs", RUN_NAME, config_path, STARTED_AT)
    with pytest.raises(ViewerClosed):
        train(LookingWatcher(closes_in_generation=2), (GenerationRecorder(recorder),))
    recorded_run = RecordedRun(recorder.run_folder_path)
    assert recorded_run.last_generation() == 1
    assert sorted(path.name for path in (recorder.run_folder_path / "generations").iterdir()) == ["0001"]
    assert len(recorder.run_folder_path.joinpath("results.csv").read_text().splitlines()) == 1 + POPULATION_SIZE


def test_headless_play_builds_no_snapshot_and_never_waits(world_1_1, monkeypatch):
    """Nothing is written and nothing paced without watching, so headless speed is unchanged."""
    def must_not_be_called(*arguments, **keywords):
        raise AssertionError("headless play did watch-live work")

    for watch_live_work in ("mario.snapshots.world_snapshot.WorldSnapshot.of",
                            "mario.snapshots.world_snapshot.AgentSnapshot.of", "time.sleep"):
        monkeypatch.setattr(watch_live_work, must_not_be_called)
    algorithm = RandomButtonsAlgorithm()
    genomes = algorithm.initial_genomes(POPULATION_SIZE, np.random.default_rng(SEED))
    started_at = time.perf_counter()
    played_attempts = ChunkPlayer(world_1_1).play(algorithm.build_brain(genomes), len(genomes))
    seconds = time.perf_counter() - started_at
    longest_attempt_ticks = max(played.attempt_result.ticks_elapsed for played in played_attempts)
    assert seconds < longest_attempt_ticks / WATCHED_TICKS_PER_SECOND / 4  # far faster than real time
