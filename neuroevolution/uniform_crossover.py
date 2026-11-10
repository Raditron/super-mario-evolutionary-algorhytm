"""Milestone 9: a child made from two parents, hoping to combine the good parts of each."""

import numpy as np

# Crossover mixes exactly two parents into one child.
PARENTS_PER_CHILD = 2
# What makes the crossover "uniform": every gene is as likely to come from one parent as from the other.
FIRST_PARENT_GENE_CHANCE = 0.5


class UniformCrossover:
    """With probability rate, each gene of the child comes from one parent or the other, chosen by a coin flip.

    Otherwise the child is a clone of the first parent. Mutation runs afterwards either way.
    Two networks can do the same job with their hidden neurons in a different order (the permutation problem),
    so mixing their genes can break both: this is an experiment, not a guaranteed improvement.
    """

    def __init__(self, rate: float) -> None:
        self._rate = rate

    def crossover(
        self, parent_a: np.ndarray, parent_b: np.ndarray, rng: np.random.Generator
    ) -> np.ndarray:
        """A new genome of the same shape, mixed from the two parents. Neither parent is changed."""
        if rng.random() >= self._rate:
            return parent_a.copy()
        takes_first_parent_gene = (
            rng.random(size=parent_a.shape) < FIRST_PARENT_GENE_CHANCE
        )
        return np.where(takes_first_parent_gene, parent_a, parent_b)
