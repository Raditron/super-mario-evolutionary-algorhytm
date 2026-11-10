"""Milestone 6: tournament selection picks parents by comparing fitnesses, favours the fitter, and only ever uses the given rng."""

import numpy as np

from neuroevolution.tournament_selection import TournamentSelection

POPULATION_SIZE = 100
# Fitness i belongs to agent i, so a higher index is a fitter agent and the quartiles are easy to read.
RISING_FITNESSES = np.arange(POPULATION_SIZE, dtype=np.float64)
TOURNAMENT_SIZE = 3
SMALL_TOURNAMENT_SIZE = 2
LARGE_TOURNAMENT_SIZE = 5
SINGLE_CONTESTANT_TOURNAMENT_SIZE = 1

SEED = 7
OTHER_SEED = 8
# Enough parents that a share measured over them sits close to its expected value.
MANY_PARENTS = 20000
FEW_PARENTS = 7

QUARTILE_START_INDEX = POPULATION_SIZE * 3 // 4
# With 3 contestants the chance that none is from the top quartile is 0.75 ** 3, so the quartile's share is about 0.58.
TOP_QUARTILE_MINIMUM_SHARE = 0.5
# With 3 contestants an agent from the bottom quartile only wins when all three are from it, about 0.016.
BOTTOM_QUARTILE_MAXIMUM_SHARE = 0.05
# With one contestant every agent is equally likely, so each has a share of 1 / POPULATION_SIZE, give or take this.
UNIFORM_SHARE_TOLERANCE = 0.005

# A strictly rising change of the numbers, standing in for the flag bonus making the fitnesses far bigger.
RESCALE_FACTOR = 1000
RESCALE_OFFSET = 20000


def make_rng(seed: int = SEED) -> np.random.Generator:
    return np.random.default_rng(seed)


def select_many(tournament_size: int, fitnesses: np.ndarray = RISING_FITNESSES, seed: int = SEED) -> np.ndarray:
    return TournamentSelection(tournament_size).select(fitnesses, MANY_PARENTS, make_rng(seed))


def test_it_gives_as_many_parent_indices_as_asked_for_and_they_are_integers():
    parent_indices = TournamentSelection(TOURNAMENT_SIZE).select(RISING_FITNESSES, FEW_PARENTS, make_rng())

    assert parent_indices.shape == (FEW_PARENTS,)
    assert np.issubdtype(parent_indices.dtype, np.integer)


def test_every_index_points_at_an_agent_in_the_population():
    parent_indices = select_many(TOURNAMENT_SIZE)

    assert parent_indices.min() >= 0
    assert parent_indices.max() < POPULATION_SIZE


def test_fitter_agents_are_picked_more_often():
    parent_indices = select_many(TOURNAMENT_SIZE)

    top_quartile_share = np.mean(parent_indices >= QUARTILE_START_INDEX)
    bottom_quartile_share = np.mean(parent_indices < POPULATION_SIZE - QUARTILE_START_INDEX)
    assert top_quartile_share > TOP_QUARTILE_MINIMUM_SHARE
    assert bottom_quartile_share < BOTTOM_QUARTILE_MAXIMUM_SHARE


def test_the_parents_are_fitter_on_average_than_the_population():
    parent_indices = select_many(TOURNAMENT_SIZE)

    assert RISING_FITNESSES[parent_indices].mean() > RISING_FITNESSES.mean()


def test_a_tournament_of_one_picks_every_agent_equally_often():
    parent_indices = select_many(SINGLE_CONTESTANT_TOURNAMENT_SIZE)

    shares = np.bincount(parent_indices, minlength=POPULATION_SIZE) / MANY_PARENTS
    assert np.all(np.abs(shares - 1 / POPULATION_SIZE) < UNIFORM_SHARE_TOLERANCE)


def test_a_larger_tournament_puts_more_selection_pressure_on_the_parents():
    small_tournament_parents = select_many(SMALL_TOURNAMENT_SIZE)
    large_tournament_parents = select_many(LARGE_TOURNAMENT_SIZE)

    assert RISING_FITNESSES[large_tournament_parents].mean() > RISING_FITNESSES[small_tournament_parents].mean()


def test_only_the_order_of_the_fitnesses_matters_not_their_size():
    rescaled_fitnesses = RISING_FITNESSES * RESCALE_FACTOR + RESCALE_OFFSET

    assert np.array_equal(select_many(TOURNAMENT_SIZE), select_many(TOURNAMENT_SIZE, rescaled_fitnesses))


def test_the_same_seed_gives_the_same_parents():
    assert np.array_equal(select_many(TOURNAMENT_SIZE, seed=SEED), select_many(TOURNAMENT_SIZE, seed=SEED))


def test_a_different_seed_gives_different_parents():
    assert not np.array_equal(select_many(TOURNAMENT_SIZE, seed=SEED), select_many(TOURNAMENT_SIZE, seed=OTHER_SEED))


def test_it_leaves_the_fitnesses_it_was_given_unchanged():
    fitnesses = RISING_FITNESSES.copy()

    TournamentSelection(TOURNAMENT_SIZE).select(fitnesses, FEW_PARENTS, make_rng())

    assert np.array_equal(fitnesses, RISING_FITNESSES)
