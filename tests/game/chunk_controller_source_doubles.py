"""Test doubles for the worker pool's seam, ChunkControllerSourceFactory (spec sections 9 and 11).

The pool sends its factory to each worker process as it starts, so these live
in a module of their own: a spawned worker imports them by name.
"""

import time
from collections.abc import Sequence

import mario.snapshots.snapshot_channel as snapshot_channel_module
from mario.level.static_level import StaticLevel
from mario.simulation.attempt import Attempt
from mario.snapshots.live_chunk_publisher import LiveChunkPublisher
from mario.training.brain_chunk_controller_source import BrainChunkControllerSourceFactory
from mario.training.chunk_controller_source import ChunkControllerSource, ChunkControllerSourceFactory
from mario.training.chunk_player import ChunkPlayer


class FixedButtonsChunkControllerSource(ChunkControllerSource):
    def __init__(self, buttons_per_agent: Sequence[int]):
        self._buttons_per_agent = list(buttons_per_agent)

    def buttons_per_agent(self, attempts: Sequence[Attempt], living_agents: Sequence[int]) -> list[int]:
        return self._buttons_per_agent


class FixedButtonsControllerSourceFactory(ChunkControllerSourceFactory):
    """No brain, no algorithm: what controls each agent is the one Controller bitmask he holds every tick."""

    def start_in_worker(self, level: StaticLevel) -> None:
        pass

    def for_chunk(self, agent_controls: Sequence[int]) -> ChunkControllerSource:
        return FixedButtonsChunkControllerSource(agent_controls)


class WatchLiveWorkFails(Exception):
    """Raised in a worker that does watch-live work while it plays headless."""


class HeadlessTripwireControllerSourceFactory(BrainChunkControllerSourceFactory):
    """Training's own factory, which also makes every piece of watch-live work fail in
    each worker it starts in: attaching shared memory, making a publisher, waiting,
    and playing a chunk with a tick listener."""

    def start_in_worker(self, level: StaticLevel) -> None:
        super().start_in_worker(level)
        play_a_chunk = ChunkPlayer.play

        def play_with_no_tick_listener(chunk_player, controller_source, agent_count, tick_listener=None):
            if tick_listener is not None:
                raise WatchLiveWorkFails(f"a headless chunk was played with a tick listener, {tick_listener!r}")
            return play_a_chunk(chunk_player, controller_source, agent_count)

        ChunkPlayer.play = play_with_no_tick_listener
        snapshot_channel_module.SharedMemory = _fails("attached the snapshot channel's shared memory")
        LiveChunkPublisher.__init__ = _fails("made a LiveChunkPublisher")
        time.sleep = _fails("waited")


def _fails(watch_live_work: str):
    def fail(*arguments, **keywords):
        raise WatchLiveWorkFails(f"a headless worker {watch_live_work}")
    return fail
