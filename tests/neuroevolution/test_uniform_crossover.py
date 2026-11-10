"""Milestone 9: uniform crossover mixes two parents gene by gene, clones the first parent the rest of the time, and only uses the given rng."""

import numpy as np

from neuroevolution.uniform_crossover import FIRST_PARENT_GENE_CHANCE, UniformCrossover

# Few enough genes that a mixed child almost surely differs from each parent, many enough to read as a mix.
SMALL_GENE_COUNT = 50
# Enough genes that the share taken from one parent sits close to its expected value.
MANY_GENES = 100_000
MANY_CHILDREN = 2000

PARENT_A_GENE_VALUE = 0.0
PARENT_B_GENE_VALUE = 1.0

MIXED_EVERY_TIME_RATE = 1.0
NEVER_MIXED_RATE = 0.0
CROSSOVER_RATE = 0.7

SEED = 7
OTHER_SEED = 8

# Over 100,000 genes the share from one parent is within 0.0016 of one half by chance, so this is a safe margin.
SHARE_TOLERANCE = 0.02
# Over 2,000 children the share that is mixed is within 0.01 of the rate by chance, so this is a safe margin.
MIXED_SHARE_TOLERANCE = 0.05


def make_rng(seed: int = SEED) -> np.random.Generator:
    return np.random.default_rng(seed)


def parent_a_of(gene_count: int) -> np.ndarray:
    return np.full(gene_count, PARENT_A_GENE_VALUE)


def parent_b_of(gene_count: int) -> np.ndarray:
    return np.full(gene_count, PARENT_B_GENE_VALUE)


def test_the_child_has_the_shape_and_type_of_the_parents():
    parent_a, parent_b = parent_a_of(SMALL_GENE_COUNT), parent_b_of(SMALL_GENE_COUNT)

    child = UniformCrossover(MIXED_EVERY_TIME_RATE).crossover(parent_a, parent_b, make_rng())

    assert child.shape == parent_a.shape
    assert child.dtype == parent_a.dtype


def test_every_gene_of_a_mixed_child_comes_from_one_of_the_parents():
    parent_a, parent_b = parent_a_of(MANY_GENES), parent_b_of(MANY_GENES)

    child = UniformCrossover(MIXED_EVERY_TIME_RATE).crossover(parent_a, parent_b, make_rng())

    assert np.all((child == PARENT_A_GENE_VALUE) | (child == PARENT_B_GENE_VALUE))


def test_a_mixed_child_takes_about_half_its_genes_from_each_parent():
    parent_a, parent_b = parent_a_of(MANY_GENES), parent_b_of(MANY_GENES)

    child = UniformCrossover(MIXED_EVERY_TIME_RATE).crossover(parent_a, parent_b, make_rng())

    share_from_the_first_parent = np.mean(child == PARENT_A_GENE_VALUE)
    assert abs(share_from_the_first_parent - FIRST_PARENT_GENE_CHANCE) < SHARE_TOLERANCE


def test_a_mixed_child_is_neither_parent():
    parent_a, parent_b = parent_a_of(SMALL_GENE_COUNT), parent_b_of(SMALL_GENE_COUNT)

    child = UniformCrossover(MIXED_EVERY_TIME_RATE).crossover(parent_a, parent_b, make_rng())

    assert not np.array_equal(child, parent_a)
    assert not np.array_equal(child, parent_b)


def test_a_rate_of_zero_gives_a_separate_clone_of_the_first_parent():
    parent_a, parent_b = parent_a_of(SMALL_GENE_COUNT), parent_b_of(SMALL_GENE_COUNT)

    child = UniformCrossover(NEVER_MIXED_RATE).crossover(parent_a, parent_b, make_rng())

    assert np.array_equal(child, parent_a)
    assert not np.shares_memory(child, parent_a)


def test_about_the_crossover_rate_of_the_children_are_mixed():
    parent_a, parent_b = parent_a_of(SMALL_GENE_COUNT), parent_b_of(SMALL_GENE_COUNT)
    crossover = UniformCrossover(CROSSOVER_RATE)
    rng = make_rng()

    children = [crossover.crossover(parent_a, parent_b, rng) for _ in range(MANY_CHILDREN)]

    mixed_share = np.mean([not np.array_equal(child, parent_a) for child in children])
    assert abs(mixed_share - CROSSOVER_RATE) < MIXED_SHARE_TOLERANCE


def test_the_child_is_a_new_array_and_the_parents_are_unchanged():
    parent_a, parent_b = parent_a_of(SMALL_GENE_COUNT), parent_b_of(SMALL_GENE_COUNT)

    child = UniformCrossover(MIXED_EVERY_TIME_RATE).crossover(parent_a, parent_b, make_rng())

    assert not np.shares_memory(child, parent_a)
    assert not np.shares_memory(child, parent_b)
    assert np.array_equal(parent_a, parent_a_of(SMALL_GENE_COUNT))
    assert np.array_equal(parent_b, parent_b_of(SMALL_GENE_COUNT))


def test_the_same_seed_gives_the_same_child():
    parent_a, parent_b = parent_a_of(SMALL_GENE_COUNT), parent_b_of(SMALL_GENE_COUNT)
    crossover = UniformCrossover(CROSSOVER_RATE)

    first = crossover.crossover(parent_a, parent_b, make_rng(SEED))
    second = crossover.crossover(parent_a, parent_b, make_rng(SEED))

    assert np.array_equal(first, second)


def test_a_different_seed_gives_a_different_child():
    parent_a, parent_b = parent_a_of(SMALL_GENE_COUNT), parent_b_of(SMALL_GENE_COUNT)
    crossover = UniformCrossover(MIXED_EVERY_TIME_RATE)

    first = crossover.crossover(parent_a, parent_b, make_rng(SEED))
    second = crossover.crossover(parent_a, parent_b, make_rng(OTHER_SEED))

    assert not np.array_equal(first, second)
