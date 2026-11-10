"""Milestone 8: the best genomes of a generation, kept unchanged so progress is never lost to an unlucky generation."""

import numpy as np


class Elitism:
    """The elite_count fittest genomes go into the next generation as they are, with no selection and no mutation.

    The game is deterministic, so an elite earns the same fitness again and the best fitness can (almost) never drop.
    On a fitness tie the lower agent index wins, the same rule the run folder uses.
    """

    def __init__(self, elite_count: int) -> None:
        self._elite_count = elite_count

    def elites(
        self, genomes: list[np.ndarray], fitnesses: np.ndarray
    ) -> list[np.ndarray]:
        """Copies of the elite_count fittest genomes, fittest first."""
        most_fit_positions = np.argsort(-fitnesses, kind="stable")
        elite_positions = most_fit_positions[: self._elite_count]

        elites: list[np.ndarray] = []
        for position in elite_positions:
            elite_genome: np.ndarray = genomes[int(position)]
            elites.append(elite_genome.copy())
        return elites