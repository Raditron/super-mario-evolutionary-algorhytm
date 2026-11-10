"""Milestone 4: random genomes have the right shape, LeCun-normal spread, zero biases, and only ever use the given rng."""

import numpy as np

from neuroevolution.constants import INPUT_SIZE, OUTPUT_SIZE
from neuroevolution.genome_layout import GenomeLayout
from neuroevolution.random_genomes import random_genome, random_genomes

HIDDEN_LAYER_SIZE = 24
REAL_LAYOUT_SIZES = [INPUT_SIZE, HIDDEN_LAYER_SIZE, OUTPUT_SIZE]
REAL_GENE_COUNT = 3989

SEED = 7
OTHER_SEED = 8
# Enough genomes that even the 24 x 5 output weights give a few thousand samples to measure the spread on.
GENOMES_FOR_THE_SPREAD = 50
# A measured spread may differ from the ideal by this share of it and still count as "about 1/sqrt(fan_in)".
SPREAD_TOLERANCE = 0.1
MEAN_TOLERANCE = 0.01


def make_rng(seed: int = SEED) -> np.random.Generator:
    return np.random.default_rng(seed)


def weights_of_layer(genomes: list[np.ndarray], layer_index: int) -> np.ndarray:
    """Every genome's weights for one layer, pooled into one flat array of samples."""
    layout = GenomeLayout(REAL_LAYOUT_SIZES)
    return np.concatenate([layout.unpack(genome)[layer_index][0].ravel() for genome in genomes])


def test_a_random_genome_is_a_flat_float_array_of_3989_genes():
    genome = random_genome(REAL_LAYOUT_SIZES, make_rng())

    assert genome.shape == (REAL_GENE_COUNT,)
    assert genome.dtype == np.float64


def test_random_genomes_gives_the_count_asked_for_each_a_full_genome():
    genomes = random_genomes(REAL_LAYOUT_SIZES, 5, make_rng())

    assert len(genomes) == 5
    assert all(genome.shape == (REAL_GENE_COUNT,) for genome in genomes)


def test_every_bias_starts_at_zero():
    layout = GenomeLayout(REAL_LAYOUT_SIZES)
    genome = random_genome(REAL_LAYOUT_SIZES, make_rng())

    for _weights, biases in layout.unpack(genome):
        assert not biases.any()


def test_the_hidden_weights_spread_is_about_one_over_root_of_the_inputs():
    genomes = random_genomes(REAL_LAYOUT_SIZES, GENOMES_FOR_THE_SPREAD, make_rng())

    hidden_weights = weights_of_layer(genomes, layer_index=0)

    ideal_spread = 1 / np.sqrt(INPUT_SIZE)
    assert abs(hidden_weights.std() - ideal_spread) < SPREAD_TOLERANCE * ideal_spread
    assert abs(hidden_weights.mean()) < MEAN_TOLERANCE


def test_the_output_weights_spread_is_about_one_over_root_of_the_hidden_neurons():
    genomes = random_genomes(REAL_LAYOUT_SIZES, GENOMES_FOR_THE_SPREAD, make_rng())

    output_weights = weights_of_layer(genomes, layer_index=1)

    ideal_spread = 1 / np.sqrt(HIDDEN_LAYER_SIZE)
    assert abs(output_weights.std() - ideal_spread) < SPREAD_TOLERANCE * ideal_spread
    assert abs(output_weights.mean()) < 5 * MEAN_TOLERANCE


def test_the_genomes_of_one_call_differ_from_each_other():
    first, second = random_genomes(REAL_LAYOUT_SIZES, 2, make_rng())

    assert not np.array_equal(first, second)


def test_the_same_seed_gives_the_same_genomes():
    first_run = random_genomes(REAL_LAYOUT_SIZES, 3, make_rng(SEED))
    second_run = random_genomes(REAL_LAYOUT_SIZES, 3, make_rng(SEED))

    for first, second in zip(first_run, second_run):
        assert np.array_equal(first, second)


def test_a_different_seed_gives_different_genomes():
    first = random_genome(REAL_LAYOUT_SIZES, make_rng(SEED))
    second = random_genome(REAL_LAYOUT_SIZES, make_rng(OTHER_SEED))

    assert not np.array_equal(first, second)
