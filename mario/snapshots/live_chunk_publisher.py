"""A worker's side of watch-live: after every tick of its chunk, it waits for that
tick's moment at the game's own speed, then publishes the chunk's snapshot
(spec section 11).

It reads the chunk's Attempts and never changes them, so it works the same
whatever their buttons come from: a brain in training, Controller logs in
all-ghost replay (#30). It only ever delays a tick, so a watched generation
plays out exactly as a headless one.
"""

import time
from collections.abc import Sequence

from mario.constants.snapshots import WATCHED_TICKS_PER_SECOND
from mario.simulation.attempt import Attempt
from mario.simulation.observation_builder import ObservationBuilder
from mario.snapshots.live_snapshots import ChunkSnapshot, followed_agent
from mario.snapshots.snapshot_channel import OpenSnapshotChannelWriter
from mario.snapshots.world_snapshot import AgentSnapshot, WorldSnapshot


class LiveChunkPublisher:
    def __init__(self, channel_writer: OpenSnapshotChannelWriter, slot: int, generation: int,
                 first_agent: int, observation_builder: ObservationBuilder):
        """first_agent: the generation's index of the chunk's first agent. The chunk's
        first tick is due one tick's time after this is made."""
        self._channel_writer = channel_writer
        self._slot = slot
        self._generation = generation
        self._first_agent = first_agent
        self._observation_builder = observation_builder
        self._followed_agent_index: int | None = None
        self._ticks_played = 0
        self._started_at = time.perf_counter()

    def tick_played(self, attempts: Sequence[Attempt]) -> None:
        """Called once the chunk's attempts (all of them, ended or not) have played a tick."""
        self._ticks_played += 1
        self._wait_for_the_ticks_moment()
        agents = [AgentSnapshot.of(self._first_agent + offset, attempt) for offset, attempt in enumerate(attempts)]
        followed = followed_agent(agents, self._followed_agent_index)
        self._followed_agent_index = followed.agent_index
        followed_world = WorldSnapshot.of(attempts[followed.agent_index - self._first_agent],
                                          observation_builder=self._observation_builder)
        self._channel_writer.write(self._slot, ChunkSnapshot(self._generation, tuple(agents), followed.agent_index,
                                                             followed_world))

    def _wait_for_the_ticks_moment(self) -> None:
        """Paced from the chunk's start, so a slow tick is made up for by the next ones."""
        seconds_early = self._started_at + self._ticks_played / WATCHED_TICKS_PER_SECOND - time.perf_counter()
        if seconds_early > 0:
            time.sleep(seconds_early)
