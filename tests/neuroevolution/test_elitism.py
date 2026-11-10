"""Milestone 8: elitism returns exactly the fittest genomes, fittest first, lower agent index first on a tie, as separate copies."""

import numpy as np

from neuroevolution.elitism import Elitism

POPULATION_SIZE = 20
GENE_COUNT = 5
ELITE_COUNT = 3
SINGLE_ELITE_COUNT = 1
WHOLE_POPULATION_ELITE_COUNT = POPULATION_SIZE
# Fitness i belongs to agent i, so a higher index is a fitter agent.
RISING_FITNESSES = np.arange(POPULATION_SIZE, dtype=np.float64)

# A population small enough to read: agents 1 and 2 tie for the best, then comes 4, then 0, then 3.
TIED_FITNESSES = np.array([5.0, 9.0, 9.0, 1.0, 7.0])
TIED_POPULATION_SIZE = len(TIED_FITNESSES)
TIED_ELITE_COUNT = 3
TIED_ELITE_AGENTS = [1, 2, 4]


def genomes_labelled_by_agent(population_size: int) -> list[np.ndarray]:
    """Genome i is full of the number i, so a genome's first gene says which agent it came from."""
    return [np.full(GENE_COUNT, float(agent_index)) for agent_index in range(population_size)]


def agents_of(genomes: list[np.ndarray]) -> list[int]:
    return [int(genome[0]) for genome in genomes]


def test_it_gives_exactly_elite_count_genomes():
    genomes = genomes_labelled_by_agent(POPULATION_SIZE)

    elites = Elitism(ELITE_COUNT).elites(genomes, RISING_FITNESSES)

    assert len(elites) == ELITE_COUNT
    assert all(elite.shape == (GENE_COUNT,) for elite in elites)


def test_the_elites_are_the_fittest_genomes_fittest_first():
    genomes = genomes_labelled_by_agent(POPULATION_SIZE)

    elites = Elitism(ELITE_COUNT).elites(genomes, RISING_FITNESSES)

    assert agents_of(elites) == [POPULATION_SIZE - 1, POPULATION_SIZE - 2, POPULATION_SIZE - 3]


def test_the_elites_do_not_depend_on_the_order_of_the_population():
    genomes = genomes_labelled_by_agent(POPULATION_SIZE)
    shuffled_order = np.random.default_rng(0).permutation(POPULATION_SIZE)
    shuffled_genomes = [genomes[position] for position in shuffled_order]
    shuffled_fitnesses = RISING_FITNESSES[shuffled_order]

    elites = Elitism(ELITE_COUNT).elites(shuffled_genomes, shuffled_fitnesses)

    assert agents_of(elites) == [POPULATION_SIZE - 1, POPULATION_SIZE - 2, POPULATION_SIZE - 3]


def test_on_a_fitness_tie_the_lower_agent_index_comes_first():
    genomes = genomes_labelled_by_agent(TIED_POPULATION_SIZE)

    elites = Elitism(TIED_ELITE_COUNT).elites(genomes, TIED_FITNESSES)

    assert agents_of(elites) == TIED_ELITE_AGENTS


def test_the_tie_rule_decides_who_gets_the_last_elite_place():
    genomes = genomes_labelled_by_agent(TIED_POPULATION_SIZE)
    tied_agent_with_the_lower_index = TIED_ELITE_AGENTS[0]

    elites = Elitism(SINGLE_ELITE_COUNT).elites(genomes, TIED_FITNESSES)

    assert agents_of(elites) == [tied_agent_with_the_lower_index]


def test_the_elites_are_copies_that_share_no_memory_with_the_population():
    genomes = genomes_labelled_by_agent(POPULATION_SIZE)

    elites = Elitism(ELITE_COUNT).elites(genomes, RISING_FITNESSES)

    for elite in elites:
        assert not any(np.shares_memory(elite, genome) for genome in genomes)


def test_it_leaves_the_population_and_the_fitnesses_unchanged():
    genomes = genomes_labelled_by_agent(POPULATION_SIZE)
    untouched_genomes = [genome.copy() for genome in genomes]
    fitnesses = RISING_FITNESSES.copy()

    Elitism(ELITE_COUNT).elites(genomes, fitnesses)

    assert np.array_equal(fitnesses, RISING_FITNESSES)
    for genome, untouched_genome in zip(genomes, untouched_genomes):
        assert np.array_equal(genome, untouched_genome)


def test_an_elite_count_equal_to_the_population_returns_everyone_best_first():
    genomes = genomes_labelled_by_agent(POPULATION_SIZE)

    elites = Elitism(WHOLE_POPULATION_ELITE_COUNT).elites(genomes, RISING_FITNESSES)

    assert agents_of(elites) == list(reversed(range(POPULATION_SIZE)))
