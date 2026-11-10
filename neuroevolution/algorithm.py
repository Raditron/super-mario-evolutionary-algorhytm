"""The algorithm the game drives through its seam (spec section 9): a network whose weights a genetic algorithm evolves."""

import numpy as np

from mario.simulation.attempt_result import AttemptResult
from mario.training.neuroevolution_algorithm import Brain, NeuroevolutionAlgorithm
from neuroevolution.algorithm_settings import AlgorithmSettings
from neuroevolution.brain import Brain as NetworkBrain
from neuroevolution.constants import INPUT_SIZE, OUTPUT_SIZE
from neuroevolution.elitism import Elitism
from neuroevolution.fitness_function import FitnessFunction
from neuroevolution.gaussian_mutation import GaussianMutation
from neuroevolution.genome_layout import GenomeLayout
from neuroevolution.layer import Layer
from neuroevolution.neural_network import NeuralNetwork
from neuroevolution.random_genomes import random_genomes
from neuroevolution.tournament_selection import TournamentSelection
from neuroevolution.uniform_crossover import PARENTS_PER_CHILD, UniformCrossover


class MarioNeuroevolution(NeuroevolutionAlgorithm):
    """Evolves the weights of a fixed-shape network: the elites carry over unchanged, and every
    other genome is a child of two tournament winners, crossed over uniformly and mutated with Gaussian noise."""

    def __init__(self, settings: AlgorithmSettings) -> None:
        self._settings = settings
        self._layer_sizes = [INPUT_SIZE, settings.hidden_layer_size, OUTPUT_SIZE]
        self._genome_layout = GenomeLayout(self._layer_sizes)
        self._fitness_function = FitnessFunction(settings)
        self._tournament_selection = TournamentSelection(settings.tournament_size)
        self._gaussian_mutation = GaussianMutation(
            settings.mutation_rate, settings.mutation_strength
        )
        self._elitism = Elitism(settings.elite_count)
        self._uniform_crossover = UniformCrossover(settings.crossover_rate)

    def initial_genomes(
        self, population_size: int, rng: np.random.Generator
    ) -> list[np.ndarray]:
        return random_genomes(self._layer_sizes, population_size, rng)

    def build_brain(self, genomes: list[np.ndarray]) -> Brain:
        networks: list[NeuralNetwork] = []
        for genome in genomes:
            layers = [
                Layer(weights, biases)
                for weights, biases in self._genome_layout.unpack(genome)
            ]
            networks.append(NeuralNetwork(layers))
        return NetworkBrain(networks, self._settings.button_press_threshold)

    def fitness(self, attempt_result: AttemptResult) -> float:
        return self._fitness_function.score(attempt_result)

    def next_genomes(
        self, genomes: list[np.ndarray], fitnesses: np.ndarray, rng: np.random.Generator
    ) -> list[np.ndarray]:
        elite_genomes: list[np.ndarray] = self._elitism.elites(genomes, fitnesses)
        child_count = len(genomes) - len(elite_genomes)
        parent_indices = self._tournament_selection.select(
            fitnesses, PARENTS_PER_CHILD * child_count, rng
        )
        first_parent_indices = parent_indices[0::PARENTS_PER_CHILD]
        second_parent_indices = parent_indices[1::PARENTS_PER_CHILD]

        mutated_children: list[np.ndarray] = []
        for first_index, second_index in zip(first_parent_indices, second_parent_indices):
            parent_a: np.ndarray = genomes[int(first_index)]
            parent_b: np.ndarray = genomes[int(second_index)]
            child = self._uniform_crossover.crossover(parent_a, parent_b, rng)
            mutated_children.append(self._gaussian_mutation.mutate(child, rng))

        return elite_genomes + mutated_children


def create_algorithm(settings: dict[str, object]) -> MarioNeuroevolution:
    """The one entry point the game imports: the [algorithm] table in, the algorithm out."""
    return MarioNeuroevolution(AlgorithmSettings.from_dict(settings))
