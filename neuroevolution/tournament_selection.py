"""Milestone 6: picks which agents become parents, by small tournaments of fitnesses."""

import numpy as np


class TournamentSelection:
    """For each parent slot, draw tournament_size agents at random and keep the fittest.

    It only compares fitnesses, so the size of the flag bonus doesn't distort it.
    A larger tournament means more selection pressure.
    """

    def __init__(self, tournament_size: int) -> None:
        self._tournament_size = tournament_size

    def select(
        self, fitnesses: np.ndarray, count: int, rng: np.random.Generator
    ) -> np.ndarray:
        """The indices of count parents, each the winner of its own tournament."""
        population_size = len(fitnesses)
        contestant_indices = rng.integers(
            0, population_size, size=(count, self._tournament_size)
        )
        contestant_fitnesses = fitnesses[contestant_indices]
        winner_columns = np.argmax(contestant_fitnesses, axis=1)
        slot_rows = np.arange(count)
        return contestant_indices[slot_rows, winner_columns]
