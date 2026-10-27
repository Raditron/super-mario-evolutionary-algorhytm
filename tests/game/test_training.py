"""The headless training loop and its worker pool, driven by the random-buttons double (#26)."""

import numpy as np
import pytest

from mario.training.agent_worker_pool import AgentWorkerPool
from mario.training.run_config import RunSettings
from mario.training.trainer import GenerationListener, GenerationReport, Trainer
from tests.game.random_buttons_algorithm import create_random_buttons_algorithm

SEED = 26
GENERATIONS = 2
POPULATION_SIZE = 20
ALL_WORKERS = 8


class GenerationCollector(GenerationListener):
    def __init__(self):
        self.reports: list[GenerationReport] = []

    def generation_finished(self, report: GenerationReport) -> None:
        self.reports.append(report)


def train(worker_count: int) -> list[GenerationReport]:
    """A run of the random-buttons double; one report per generation."""
    collector = GenerationCollector()
    run_settings = RunSettings(name="test", seed=SEED, generations=GENERATIONS, population_size=POPULATION_SIZE)
    with AgentWorkerPool(create_random_buttons_algorithm, {}, worker_count) as worker_pool:
        Trainer(create_random_buttons_algorithm({}), worker_pool, run_settings, collector).run()
    return collector.reports


@pytest.fixture(scope="module")
def run_on_all_workers() -> list[GenerationReport]:
    return train(ALL_WORKERS)


def test_every_agent_of_every_generation_gets_an_attempt_result_and_a_controller_log(run_on_all_workers):
    assert [report.generation for report in run_on_all_workers] == [1, 2]
    for report in run_on_all_workers:
        assert len(report.played_attempts) == POPULATION_SIZE
        for played_attempt in report.played_attempts:
            assert played_attempt.controller_log.dtype == np.uint8
            assert len(played_attempt.controller_log) == played_attempt.attempt_result.ticks_elapsed
