"""Where a chunk's agents get their Controller buttons in a worker: the worker pool's one seam
with what controls them (spec sections 9 and 11).

The pool and its ChunkPlayer only ever ask a ChunkControllerSource for each
agent's buttons, tick after tick; they never know what decides them. Training's
is a brain built from the chunk's genomes (BrainChunkControllerSourceFactory);
all-ghost replay (#30) gives the pool ControllerLogChunkControllerSourceFactory, whose sources
play Controller logs back, with no algorithm built.
"""

from abc import ABC, abstractmethod
from collections.abc import Sequence

from mario.level.static_level import StaticLevel
from mario.simulation.attempt import Attempt


class ChunkControllerSource(ABC):
    @abstractmethod
    def buttons_per_agent(self, attempts: Sequence[Attempt], living_agents: Sequence[int]) -> list[int]:
        """This tick's Controller bitmask of every agent of the chunk, by his place in it.

        attempts: every attempt of the chunk, ended or not, read only. Only the
        living agents' buttons are pressed."""


class ChunkControllerSourceFactory(ABC):
    """Picklable: the pool sends it to each worker process as that starts, then
    hands it what controls each agent of a chunk (training: their genomes), in
    agent order."""

    @abstractmethod
    def start_in_worker(self, level: StaticLevel) -> None:
        """Called once in each worker process as it starts, before any chunk: builds
        what that process's chunks share. Raises, its message saying why, if it can't."""

    @abstractmethod
    def for_chunk(self, agent_controls: Sequence) -> ChunkControllerSource:
        """The source of one chunk's buttons, row i for agent i of agent_controls."""
