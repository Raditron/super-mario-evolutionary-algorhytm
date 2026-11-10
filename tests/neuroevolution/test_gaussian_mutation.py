"""Milestone 7: Gaussian mutation nudges about rate of the genes by Normal(0, strength), never touches the parent, and only uses the given rng."""

import numpy as np
import pytest

from neuroevolution.gaussian_mutation import GaussianMutation

GENE_COUNT = 3989
# Enough genes that a share or a spread measured over the mutated ones sits close to its expected value.
MANY_GENES = 100_000

RATE = 0.05
STRENGTH = 0.05
OTHER_STRENGTH = 0.2
NO_MUTATION_RATE = 0.0
EVERY_GENE_RATE = 1.0

PARENT_GENE_VALUE = 1.0
SEED = 7
OTHER_SEED = 8

# 3989 genes at a 5% rate change 199 of them give or take 14 by chance, so 30% of the expectation is over 4 sigma.
MUTATED_COUNT_TOLERANCE = 0.3
# Over 100,000 genes the spread of the changes is pinned down to about 1%, so 10% is a safe margin.
SPREAD_TOLERANCE = 0.1
# The mean of about 5,000 changes is within 0.0007 of 0 by chance, so this is a safe margin.
MEAN_TOLERANCE = 0.005
# Normal(0, strength) almost never goes past 6 strengths, but replacing a gene with noise would leave it a whole 1.0 off.
LARGEST_NUDGE_IN_STRENGTHS = 6


def make_rng(seed: int = SEED) -> np.random.Generator:
    return np.random.default_rng(seed)


def parent_of(gene_count: int) -> np.ndarray:
    return np.full(gene_count, PARENT_GENE_VALUE)


def test_the_child_has_the_shape_and_type_of_the_parent():
    parent = parent_of(GENE_COUNT)

    child = GaussianMutation(RATE, STRENGTH).mutate(parent, make_rng())

    assert child.shape == parent.shape
    assert child.dtype == parent.dtype


def test_the_child_is_a_new_array_and_the_parent_is_unchanged():
    parent = parent_of(GENE_COUNT)
    untouched_parent = parent.copy()

    child = GaussianMutation(RATE, STRENGTH).mutate(parent, make_rng())

    assert not np.shares_memory(child, parent)
    assert np.array_equal(parent, untouched_parent)


def test_about_rate_times_the_gene_count_of_the_genes_change():
    parent = parent_of(GENE_COUNT)

    child = GaussianMutation(RATE, STRENGTH).mutate(parent, make_rng())

    expected_changed_genes = RATE * GENE_COUNT
    changed_genes = np.count_nonzero(child != parent)
    assert abs(changed_genes - expected_changed_genes) < MUTATED_COUNT_TOLERANCE * expected_changed_genes


@pytest.mark.parametrize("strength", [STRENGTH, OTHER_STRENGTH])
def test_the_changes_are_centred_on_zero_with_a_spread_of_the_strength(strength):
    parent = parent_of(MANY_GENES)

    child = GaussianMutation(RATE, strength).mutate(parent, make_rng())

    changes = (child - parent)[child != parent]
    assert abs(changes.mean()) < MEAN_TOLERANCE
    assert abs(changes.std() - strength) < SPREAD_TOLERANCE * strength


def test_a_gene_is_nudged_not_replaced():
    parent = parent_of(MANY_GENES)

    child = GaussianMutation(RATE, STRENGTH).mutate(parent, make_rng())

    assert np.abs(child - parent).max() < LARGEST_NUDGE_IN_STRENGTHS * STRENGTH


def test_genes_can_go_both_up_and_down():
    parent = parent_of(GENE_COUNT)

    child = GaussianMutation(RATE, STRENGTH).mutate(parent, make_rng())

    assert (child > parent).any()
    assert (child < parent).any()


def test_a_rate_of_zero_gives_an_identical_but_separate_child():
    parent = parent_of(GENE_COUNT)

    child = GaussianMutation(NO_MUTATION_RATE, STRENGTH).mutate(parent, make_rng())

    assert np.array_equal(child, parent)
    assert not np.shares_memory(child, parent)


def test_a_rate_of_one_changes_every_gene():
    parent = parent_of(GENE_COUNT)

    child = GaussianMutation(EVERY_GENE_RATE, STRENGTH).mutate(parent, make_rng())

    assert np.all(child != parent)


def test_the_same_seed_gives_the_same_child():
    parent = parent_of(GENE_COUNT)
    mutation = GaussianMutation(RATE, STRENGTH)

    assert np.array_equal(mutation.mutate(parent, make_rng(SEED)), mutation.mutate(parent, make_rng(SEED)))


def test_a_different_seed_gives_a_different_child():
    parent = parent_of(GENE_COUNT)
    mutation = GaussianMutation(RATE, STRENGTH)

    assert not np.array_equal(mutation.mutate(parent, make_rng(SEED)), mutation.mutate(parent, make_rng(OTHER_SEED)))
