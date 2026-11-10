"""Milestone 4: genomes drawn at random, for the first generation and for random search (the baseline to beat)."""

import numpy as np

from neuroevolution.genome_layout import GenomeLayout, LayerParameters


def random_genome(layer_sizes: list[int], rng: np.random.Generator) -> np.ndarray:
    """One flat genome: every weight drawn from Normal(0, 1 / sqrt(fan_in)) (LeCun normal), every bias 0.

    fan_in is the number of inputs of the neuron the weight feeds, so it is the layer's input_count.
    """
    layers_parameters: list[LayerParameters] = []
    for input_count, neuron_count in zip(layer_sizes, layer_sizes[1:]):
        spread = 1 / np.sqrt(input_count)
        weights = rng.normal(0, spread, size=(input_count, neuron_count))
        biases = np.zeros(neuron_count)
        layers_parameters.append((weights, biases))
    return GenomeLayout(layer_sizes).pack(layers_parameters)


def random_genomes(
    layer_sizes: list[int], count: int, rng: np.random.Generator
) -> list[np.ndarray]:
    """count independent random genomes, drawn one after another from the same rng."""
    genomes: list[np.ndarray] = []
    for _ in range(count):
        genomes.append(random_genome(layer_sizes, rng))
    return genomes
