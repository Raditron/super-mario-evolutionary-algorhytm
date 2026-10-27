"""The generation loop of one run (spec section 9, ADR 0001).

The algorithm is injected. The Trainer makes the run's one random generator
from its seed, has the worker pool play each generation, scores each attempt
with the algorithm's fitness, reports the generation, and asks the algorithm
for the next genomes.
"""

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np

from mario.controller.brain_controller_source import PlayedAttempt
from mario.training.agent_worker_pool import AgentWorkerPool
from mario.training.neuroevolution_algorithm import NeuroevolutionAlgorithm
from mario.training.run_config import RunSettings


@dataclass(frozen=True)
class GenerationReport:
    """One finished generation. Every list lines up by agent index."""
    generation: int
    genomes: list[np.ndarray]
    played_attempts: list[PlayedAttempt]
    fitnesses: np.ndarray
    seconds: float


class GenerationListener(ABC):
    @abstractmethod
    def generation_finished(self, report: GenerationReport) -> None:
        """Called once per generation, after it has been played and scored."""


class Trainer:
    def __init__(self, algorithm: NeuroevolutionAlgorithm, worker_pool: AgentWorkerPool,
                 run_settings: RunSettings, generation_listener: GenerationListener):
        self._algorithm = algorithm
        self._worker_pool = worker_pool
        self._run_settings = run_settings
        self._generation_listener = generation_listener

    def run(self) -> None:
        rng = np.random.default_rng(self._run_settings.seed)
        genomes = self._algorithm.initial_genomes(self._run_settings.population_size, rng)
        for generation in range(1, self._run_settings.generations + 1):
            report = self._play_generation(generation, genomes)
            self._generation_listener.generation_finished(report)
            if generation < self._run_settings.generations:
                genomes = self._algorithm.next_genomes(genomes, report.fitnesses, rng)

    def _play_generation(self, generation: int, genomes: list[np.ndarray]) -> GenerationReport:
        if len(genomes) != self._run_settings.population_size:
            raise ValueError(f"the algorithm gave {len(genomes)} genomes for a population of "
                             f"{self._run_settings.population_size}")
        started_at = time.perf_counter()
        played_attempts = self._worker_pool.play(genomes)
        fitnesses = np.array([self._algorithm.fitness(played_attempt.attempt_result)
                              for played_attempt in played_attempts], dtype=np.float64)
        return GenerationReport(generation, genomes, played_attempts, fitnesses, time.perf_counter() - started_at)
