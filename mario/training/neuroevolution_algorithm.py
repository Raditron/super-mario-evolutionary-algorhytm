"""The seam with the user's algorithm (spec section 9, ADR 0001).

The game runs the generation loop and calls the user's code only through these
two types. The user's package implements them and exposes
create_algorithm(settings: dict) -> NeuroevolutionAlgorithm.
"""

from abc import ABC, abstractmethod
from typing import Protocol

import numpy as np

from mario.simulation.attempt_result import AttemptResult


class Brain(Protocol):
    def decide(self, observations: np.ndarray) -> np.ndarray:
        """(agents x 160) float64 -> (agents x 5) bool, columns in Controller order.

        Row i is always agent i of the genomes the brain was built from, every
        tick, until the last of their attempts ends: a row whose attempt has
        already ended repeats that attempt's last Observation, and its answer is
        ignored."""


class NeuroevolutionAlgorithm(ABC):
    @abstractmethod
    def initial_genomes(self, population_size: int, rng: np.random.Generator) -> list[np.ndarray]:
        """The first generation's genomes, one flat 1-D float array per agent."""

    @abstractmethod
    def build_brain(self, genomes: list[np.ndarray]) -> Brain:
        """One brain that decides for all these agents at once, row i for genome i."""

    @abstractmethod
    def fitness(self, attempt_result: AttemptResult) -> float:
        """The fitness an agent earns for its attempt."""

    @abstractmethod
    def next_genomes(self, genomes: list[np.ndarray], fitnesses: np.ndarray,
                     rng: np.random.Generator) -> list[np.ndarray]:
        """The next generation's genomes; fitnesses lines up with genomes by agent index."""
