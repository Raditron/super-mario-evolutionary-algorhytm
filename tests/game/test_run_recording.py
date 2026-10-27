"""The run folder (#27, spec section 10): what a run records, driven by the Trainer.

The run folder's files are the interface here: replay and stats read nothing else.
"""

import csv
from datetime import datetime
from pathlib import Path

import numpy as np
import pytest

from mario.recording.run_recorder import RunRecorder
from mario.training.agent_worker_pool import AgentWorkerPool
from mario.training.algorithm_factory import AlgorithmFactory
from mario.training.generation_recorder import GenerationRecorder
from mario.training.run_config import RunSettings
from mario.training.trainer import GenerationListener, GenerationReport, Trainer
from tests.game.random_buttons_algorithm import create_random_buttons_algorithm

SEED = 27
GENERATIONS = 2
POPULATION_SIZE = 6
WORKER_COUNT = 2
RUN_NAME = "recorded"
STARTED_AT = datetime(2026, 10, 27, 14, 5)
RUN_FOLDER_NAME = "2026-10-27_14-05_recorded"
CONFIG_TEXT = '[run]\nname = "recorded"\n\n[algorithm]\nmutation = 0.1\n'
RESULTS_HEADER = ["generation", "agent", "fitness", "end_reason", "furthest_x", "ticks_elapsed",
                  "final_score", "coins_collected"]
GENERATION_TIMES_HEADER = ["generation", "seconds"]


class GenerationCollector(GenerationListener):
    def __init__(self):
        self.reports: list[GenerationReport] = []

    def generation_finished(self, report: GenerationReport) -> None:
        self.reports.append(report)


def read_rows(csv_path: Path) -> list[list[str]]:
    with csv_path.open(newline="") as csv_file:
        return list(csv.reader(csv_file))


def files_under(folder: Path) -> set[str]:
    return {path.relative_to(folder).as_posix() for path in folder.rglob("*") if path.is_file()}


def start_recorder(tmp_path: Path) -> RunRecorder:
    config_path = tmp_path / "config.toml"
    config_path.write_text(CONFIG_TEXT)
    return RunRecorder.start(tmp_path / "runs", RUN_NAME, config_path, STARTED_AT)


def record_a_run(tmp_path: Path) -> tuple[Path, list[GenerationReport]]:
    """A 2-generation run of the random-buttons double; its run folder and its reports."""
    recorder = start_recorder(tmp_path)
    collector = GenerationCollector()
    run_settings = RunSettings(name=RUN_NAME, seed=SEED, generations=GENERATIONS, population_size=POPULATION_SIZE)
    algorithm_factory = AlgorithmFactory(create_random_buttons_algorithm, {})
    with AgentWorkerPool(algorithm_factory, WORKER_COUNT) as worker_pool:
        Trainer(algorithm_factory.create(), worker_pool, run_settings,
                [GenerationRecorder(recorder), collector]).run()
    return recorder.run_folder, collector.reports


@pytest.fixture(scope="module")
def recorded_run(tmp_path_factory) -> tuple[Path, list[GenerationReport]]:
    return record_a_run(tmp_path_factory.mktemp("run"))


def test_a_two_generation_run_writes_exactly_the_run_folder_layout(recorded_run):
    run_folder, _ = recorded_run
    assert run_folder.name == RUN_FOLDER_NAME
    assert files_under(run_folder) == {
        "config.toml", "results.csv", "generation_times.csv",
        "generations/0001/controller_logs.npz", "generations/0001/best_genome.npy",
        "generations/0002/controller_logs.npz", "generations/0002/best_genome.npy",
    }
    assert (run_folder / "config.toml").read_text() == CONFIG_TEXT
