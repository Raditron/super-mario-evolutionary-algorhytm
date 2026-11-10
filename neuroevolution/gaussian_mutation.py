"""Milestone 7: small random changes to a genome, so a child can be better than its parent."""

import numpy as np


class GaussianMutation:
    """Each gene, with probability rate, gets a number drawn from Normal(0, strength) added.

    Too strong and children are random; too weak and progress crawls (exploration vs exploitation).
    """

    def __init__(self, rate: float, strength: float) -> None:
        self._rate = rate
        self._strength = strength

    def mutate(self, genome: np.ndarray, rng: np.random.Generator) -> np.ndarray:
        """A new genome of the same shape: the parent with some genes nudged. The parent is never changed."""
        new_genome = genome.copy()
        chance_per_gene = rng.random(size=genome.shape)
        chosen_genes = chance_per_gene < self._rate
        noise = rng.normal(0, self._strength, size=genome.shape)
        """chosen genes is an arr of 1,0 - 1 for chosen, 0for not, 
        entirely randomized - we multiply the genome copy with the chosen ones -
          genomes who are false are multiplied by 0 so they dont changed, genomes chosen are multiplied by  * (1 * noise), 
          so they actually mutate"""
        new_genome = new_genome + chosen_genes * noise
        return new_genome
