"""Milestones 4, 6 and 7: the algorithm the game drives makes random genomes, builds a brain from them, plays them,
and hands the next generation over as mutated copies of tournament-selected parents.
"""

import tomllib
from pathlib import Path

import numpy as np

from mario.training.neuroevolution_algorithm import NeuroevolutionAlgorithm
from neuroevolution import create_algorithm
from neuroevolution.constants import INPUT_SIZE, OUTPUT_SIZE
from neuroevolution.uniform_crossover import PARENTS_PER_CHILD

CONFIG_PATH = Path(__file__).resolve().parents[2] / "config.toml"
REAL_GENE_COUNT = 3989

SEED = 11
POPULATION_SIZE = 6
AGENT_COUNT = 3
# Enough agents that the fitter parents' advantage stands well clear of chance.
SELECTION_POPULATION_SIZE = 200
# With tournaments of 3 the parents' mean index is about 150 against the population's 100, so 20 is a safe margin.
PARENT_ADVANTAGE_MARGIN = 20
# 3989 genes at a 5% rate change 199 of them give or take 14 by chance, so 30% of the expectation is over 4 sigma.
MUTATED_COUNT_TOLERANCE = 0.3
# The crossover rate of 0.7 mixes about 70% of the children, so over half is a safe margin.
MIXED_CHILDREN_MINIMUM_SHARE = 0.5


def algorithm_table() -> dict[str, object]:
    with CONFIG_PATH.open("rb") as config_file:
        return tomllib.load(config_file)["algorithm"]


def real_algorithm() -> NeuroevolutionAlgorithm:
    return create_algorithm(algorithm_table())


def make_rng(seed: int = SEED) -> np.random.Generator:
    return np.random.default_rng(seed)


def random_observations(agent_count: int) -> np.ndarray:
    return make_rng().standard_normal((agent_count, INPUT_SIZE))


def test_initial_genomes_are_one_full_flat_genome_per_agent():
    genomes = real_algorithm().initial_genomes(POPULATION_SIZE, make_rng())

    assert len(genomes) == POPULATION_SIZE
    assert all(genome.shape == (REAL_GENE_COUNT,) for genome in genomes)


def test_initial_genomes_differ_from_each_other():
    first, second, *_rest = real_algorithm().initial_genomes(POPULATION_SIZE, make_rng())

    assert not np.array_equal(first, second)


def test_the_same_seed_gives_the_same_initial_genomes():
    first_run = real_algorithm().initial_genomes(POPULATION_SIZE, make_rng(SEED))
    second_run = real_algorithm().initial_genomes(POPULATION_SIZE, make_rng(SEED))

    for first, second in zip(first_run, second_run):
        assert np.array_equal(first, second)


def test_the_brain_answers_with_one_row_of_five_bools_per_agent():
    algorithm = real_algorithm()
    genomes = algorithm.initial_genomes(AGENT_COUNT, make_rng())

    presses = algorithm.build_brain(genomes).decide(random_observations(AGENT_COUNT))

    assert presses.shape == (AGENT_COUNT, OUTPUT_SIZE)
    assert presses.dtype == np.bool_


def test_row_i_of_the_brain_is_decided_by_genome_i():
    algorithm = real_algorithm()
    genomes = algorithm.initial_genomes(AGENT_COUNT, make_rng())
    observations = random_observations(AGENT_COUNT)

    together = algorithm.build_brain(genomes).decide(observations)

    for agent_index, genome in enumerate(genomes):
        alone = algorithm.build_brain([genome]).decide(observations[agent_index : agent_index + 1])
        assert together[agent_index].tolist() == alone[0].tolist()


def test_an_all_zero_genome_presses_nothing():
    algorithm = real_algorithm()
    silent_genome = np.zeros(REAL_GENE_COUNT)

    presses = algorithm.build_brain([silent_genome]).decide(random_observations(1))

    assert not presses.any()


def rising_fitnesses(population_size: int) -> np.ndarray:
    """Agent i scores i, so a higher index is a fitter agent."""
    return np.arange(population_size, dtype=np.float64)


def genomes_labelled_by_agent(population_size: int) -> list[np.ndarray]:
    """Genome i is full of the number i, so a child's first gene says which parent it was copied from."""
    return [np.full(REAL_GENE_COUNT, float(agent_index)) for agent_index in range(population_size)]


def test_next_genomes_keep_the_population_size_and_the_gene_count():
    algorithm = real_algorithm()
    genomes = algorithm.initial_genomes(POPULATION_SIZE, make_rng())

    next_genomes = algorithm.next_genomes(genomes, rising_fitnesses(POPULATION_SIZE), make_rng(SEED + 1))

    assert len(next_genomes) == POPULATION_SIZE
    assert all(genome.shape == (REAL_GENE_COUNT,) for genome in next_genomes)


def test_the_best_genomes_lead_the_next_generation_unchanged_fittest_first():
    algorithm = real_algorithm()
    genomes = algorithm.initial_genomes(SELECTION_POPULATION_SIZE, make_rng())
    elite_count = algorithm_table()["elite_count"]

    next_genomes = algorithm.next_genomes(genomes, rising_fitnesses(SELECTION_POPULATION_SIZE), make_rng(SEED + 1))

    for rank in range(elite_count):
        fittest_remaining_genome = genomes[SELECTION_POPULATION_SIZE - 1 - rank]
        assert np.array_equal(next_genomes[rank], fittest_remaining_genome)


def test_every_genome_after_the_elites_mixes_at_most_two_genomes_of_the_old_generation():
    algorithm = real_algorithm()
    genomes = genomes_labelled_by_agent(SELECTION_POPULATION_SIZE)
    elite_count = algorithm_table()["elite_count"]

    next_genomes = algorithm.next_genomes(genomes, rising_fitnesses(SELECTION_POPULATION_SIZE), make_rng(SEED + 1))

    # A gene copied from agent i is i; mutation only nudges it by a few hundredths, so rounding recovers the agent.
    for child in next_genomes[elite_count:]:
        assert len(np.unique(np.round(child))) <= PARENTS_PER_CHILD


def test_most_children_really_mix_two_different_genomes_of_the_old_generation():
    algorithm = real_algorithm()
    genomes = genomes_labelled_by_agent(SELECTION_POPULATION_SIZE)
    elite_count = algorithm_table()["elite_count"]

    next_genomes = algorithm.next_genomes(genomes, rising_fitnesses(SELECTION_POPULATION_SIZE), make_rng(SEED + 1))

    children = next_genomes[elite_count:]
    mixed_children = [child for child in children if len(np.unique(np.round(child))) == PARENTS_PER_CHILD]
    assert len(mixed_children) / len(children) > MIXED_CHILDREN_MINIMUM_SHARE


def test_about_the_mutation_rate_of_the_genes_of_each_child_are_mutated():
    algorithm = real_algorithm()
    genomes = genomes_labelled_by_agent(SELECTION_POPULATION_SIZE)
    table = algorithm_table()
    elite_count = table["elite_count"]
    expected_mutated_genes = table["mutation_rate"] * REAL_GENE_COUNT

    next_genomes = algorithm.next_genomes(genomes, rising_fitnesses(SELECTION_POPULATION_SIZE), make_rng(SEED + 1))

    # An unmutated gene is still exactly the whole number of the agent it came from.
    for child in next_genomes[elite_count:]:
        mutated_genes = np.count_nonzero(child != np.round(child))
        assert abs(mutated_genes - expected_mutated_genes) < MUTATED_COUNT_TOLERANCE * expected_mutated_genes


def test_the_children_are_not_clones_of_any_old_genome():
    algorithm = real_algorithm()
    genomes = algorithm.initial_genomes(SELECTION_POPULATION_SIZE, make_rng())
    elite_count = algorithm_table()["elite_count"]

    next_genomes = algorithm.next_genomes(genomes, rising_fitnesses(SELECTION_POPULATION_SIZE), make_rng(SEED + 1))

    for child in next_genomes[elite_count:]:
        assert not any(np.array_equal(child, genome) for genome in genomes)


def test_the_next_generation_is_as_large_as_the_old_one_with_the_elites_in_it():
    algorithm = real_algorithm()
    genomes = algorithm.initial_genomes(SELECTION_POPULATION_SIZE, make_rng())

    next_genomes = algorithm.next_genomes(genomes, rising_fitnesses(SELECTION_POPULATION_SIZE), make_rng(SEED + 1))

    assert len(next_genomes) == SELECTION_POPULATION_SIZE


def test_next_genomes_share_no_memory_with_the_old_ones():
    algorithm = real_algorithm()
    genomes = algorithm.initial_genomes(POPULATION_SIZE, make_rng())

    next_genomes = algorithm.next_genomes(genomes, rising_fitnesses(POPULATION_SIZE), make_rng(SEED + 1))

    for next_genome in next_genomes:
        assert not any(np.shares_memory(next_genome, genome) for genome in genomes)


def test_next_genomes_leave_the_old_generation_unchanged():
    algorithm = real_algorithm()
    genomes = algorithm.initial_genomes(POPULATION_SIZE, make_rng())
    untouched_genomes = [genome.copy() for genome in genomes]

    algorithm.next_genomes(genomes, rising_fitnesses(POPULATION_SIZE), make_rng(SEED + 1))

    for genome, untouched_genome in zip(genomes, untouched_genomes):
        assert np.array_equal(genome, untouched_genome)


def test_fitter_agents_are_chosen_as_parents_more_often():
    algorithm = real_algorithm()
    genomes = genomes_labelled_by_agent(SELECTION_POPULATION_SIZE)
    fitnesses = rising_fitnesses(SELECTION_POPULATION_SIZE)

    next_genomes = algorithm.next_genomes(genomes, fitnesses, make_rng(SEED + 1))

    parent_indices = np.array([next_genome[0] for next_genome in next_genomes])
    assert parent_indices.mean() > fitnesses.mean() + PARENT_ADVANTAGE_MARGIN


def test_the_same_seed_gives_the_same_next_generation():
    algorithm = real_algorithm()
    genomes = algorithm.initial_genomes(POPULATION_SIZE, make_rng())
    fitnesses = rising_fitnesses(POPULATION_SIZE)

    first_run = algorithm.next_genomes(genomes, fitnesses, make_rng(SEED + 1))
    second_run = algorithm.next_genomes(genomes, fitnesses, make_rng(SEED + 1))

    for first, second in zip(first_run, second_run):
        assert np.array_equal(first, second)
