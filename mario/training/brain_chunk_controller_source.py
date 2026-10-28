"""Training's ChunkControllerSource: one brain, built from the chunk's genomes, decides
for all of its agents at once, every tick (spec section 9, ADR 0001).

Every tick, the living agents' Observations are built as one batch, and the
brain gets one row per agent of the chunk: an ended agent's row keeps his last
Observation, and its answer is ignored.
"""

from collections.abc import Sequence

import numpy as np

from mario.constants.observation import OBSERVATION_LENGTH
from mario.controller.brain_controller_source import BrainControllerSource
from mario.level.static_level import StaticLevel
from mario.simulation.attempt import Attempt
from mario.simulation.observation_builder import ObservationBuilder
from mario.training.algorithm_factory import AlgorithmFactory
from mario.training.chunk_controller_source import ChunkControllerSource, ChunkControllerSourceFactory
from mario.training.neuroevolution_algorithm import Brain, NeuroevolutionAlgorithm


class BrainChunkControllerSource(ChunkControllerSource):
    def __init__(self, brain: Brain, agent_count: int, observation_builder: ObservationBuilder):
        self._brain = brain
        self._controller_source = BrainControllerSource(agent_count)
        self._observation_builder = observation_builder
        self._observations = np.empty((agent_count, OBSERVATION_LENGTH), dtype=np.float64)

    def buttons_per_agent(self, attempts: Sequence[Attempt], living_agents: Sequence[int]) -> list[int]:
        self._observations[living_agents] = self._observation_builder.build_batch(
            [attempts[agent] for agent in living_agents])
        return self._controller_source.buttons_per_agent(self._brain.decide(self._observations))


class BrainChunkControllerSourceFactory(ChunkControllerSourceFactory):
    """Each worker builds the user's algorithm once, through the same create_algorithm
    the main process uses, then each chunk's brain from its genomes."""

    def __init__(self, algorithm_factory: AlgorithmFactory):
        self._algorithm_factory = algorithm_factory
        self._algorithm: NeuroevolutionAlgorithm | None = None
        self._observation_builder: ObservationBuilder | None = None

    def start_in_worker(self, level: StaticLevel) -> None:
        try:
            self._algorithm = self._algorithm_factory.create()
        except Exception as problem:  # the user's code, half-written
            raise RuntimeError(f"create_algorithm(settings) failed in a worker process "
                               f"({type(problem).__name__}: {problem})") from problem
        self._observation_builder = ObservationBuilder(level)

    def for_chunk(self, agent_controls: Sequence[np.ndarray]) -> ChunkControllerSource:
        """agent_controls: the chunk's genomes."""
        return BrainChunkControllerSource(self._algorithm.build_brain(list(agent_controls)), len(agent_controls),
                                          self._observation_builder)
