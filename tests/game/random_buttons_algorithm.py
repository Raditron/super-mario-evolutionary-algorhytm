"""A test double for the user's algorithm: every agent presses random buttons.

It is not a neural network and not a genetic algorithm (those are the user's to
write). A genome is just the seed of its agent's own random button stream, so
an agent presses the same buttons whichever worker or chunk plays it.
"""

import numpy as np

from mario.constants.controller import CONTROLLER_BUTTONS
from mario.simulation.attempt_result import AttemptResult
from mario.training.neuroevolution_algorithm import Brain, NeuroevolutionAlgorithm

# Each button is held on a tick with this probability.
BUTTON_PRESS_PROBABILITY = 0.5
# Seeds are drawn below this, so a float64 genome holds them exactly.
SEED_LIMIT = 2 ** 31


class RandomButtonsBrain:
    def __init__(self, genomes: list[np.ndarray]):
        self._button_streams = [np.random.default_rng(int(genome[0])) for genome in genomes]

    def decide(self, observations: np.ndarray) -> np.ndarray:
        if len(observations) != len(self._button_streams):
            raise ValueError(f"{len(observations)} Observations for {len(self._button_streams)} agents")
        return np.array([stream.random(len(CONTROLLER_BUTTONS)) < BUTTON_PRESS_PROBABILITY
                         for stream in self._button_streams])


class RandomButtonsAlgorithm(NeuroevolutionAlgorithm):
    def initial_genomes(self, population_size: int, rng: np.random.Generator) -> list[np.ndarray]:
        return self._fresh_seeds(population_size, rng)

    def build_brain(self, genomes: list[np.ndarray]) -> Brain:
        return RandomButtonsBrain(genomes)

    def fitness(self, attempt_result: AttemptResult) -> float:
        return float(attempt_result.furthest_x)

    def next_genomes(self, genomes: list[np.ndarray], fitnesses: np.ndarray,
                     rng: np.random.Generator) -> list[np.ndarray]:
        """Nothing is inherited: every agent of the next generation gets a fresh seed."""
        return self._fresh_seeds(len(genomes), rng)

    @staticmethod
    def _fresh_seeds(agent_count: int, rng: np.random.Generator) -> list[np.ndarray]:
        return [np.array([seed], dtype=np.float64) for seed in rng.integers(SEED_LIMIT, size=agent_count)]


def create_random_buttons_algorithm(settings: dict) -> RandomButtonsAlgorithm:
    """Stands in for neuroevolution.create_algorithm; the settings are ignored."""
    return RandomButtonsAlgorithm()
