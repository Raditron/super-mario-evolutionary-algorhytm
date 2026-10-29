"""Watch-live's hand-over: each worker writes its chunk's snapshot into shared memory every tick,
paced to the game's own speed (#29, spec section 11)."""

import time

import pytest

from mario.constants.snapshots import WATCHED_TICKS_PER_SECOND
from mario.level.static_level import StaticLevel
from mario.simulation.attempt import Attempt
from mario.simulation.observation_builder import ObservationBuilder
from mario.snapshots.live_chunk_publisher import LiveChunkPublisher
from mario.snapshots.snapshot_channel import SnapshotChannel
from mario.snapshots.world_snapshot import MarioPose, WorldSnapshot
from tests.game.helpers import HOLD_LEFT, HOLD_NOTHING, HOLD_RIGHT

SLOT_COUNT = 3
SLOT = 1
GENERATION = 2
FIRST_AGENT = 40
PACED_TICKS = 30
TICKS_TO_MOVE_A_FEW_PIXELS = 20


@pytest.fixture
def channel():
    channel = SnapshotChannel(SLOT_COUNT)
    yield channel
    channel.close()


def test_slots_not_yet_written_read_back_as_none(channel):
    assert channel.read_all() == [None] * SLOT_COUNT


def test_the_snapshot_a_chunk_writes_into_its_slot_is_read_back_whole(channel, world_1_1: StaticLevel):
    attempts = [Attempt(world_1_1, ends_on_stall=True) for _ in range(2)]
    for _ in range(TICKS_TO_MOVE_A_FEW_PIXELS):
        attempts[0].step(HOLD_NOTHING)
        attempts[1].step(HOLD_RIGHT)
    publisher = LiveChunkPublisher(channel.writer.open(), SLOT, GENERATION, FIRST_AGENT,
                                   ObservationBuilder(world_1_1))
    publisher.tick_played(attempts)
    [first, published, last] = channel.read_all()
    assert first is None and last is None
    assert published.generation == GENERATION
    assert [agent.agent_index for agent in published.agents] == [FIRST_AGENT, FIRST_AGENT + 1]
    # the chunk's followed agent is its rightmost, with his whole world and Observation
    assert published.followed_agent_index == FIRST_AGENT + 1
    assert published.followed_world == WorldSnapshot.of(attempts[1], observation_builder=ObservationBuilder(world_1_1))
    assert published.followed_world.observation is not None


def test_the_slot_carries_which_way_each_agent_faces(channel, world_1_1: StaticLevel):
    attempts = [Attempt(world_1_1, ends_on_stall=True) for _ in range(2)]
    for _ in range(TICKS_TO_MOVE_A_FEW_PIXELS):
        attempts[0].step(HOLD_LEFT)
        attempts[1].step(HOLD_RIGHT)
    publisher = LiveChunkPublisher(channel.writer.open(), SLOT, GENERATION, FIRST_AGENT,
                                   ObservationBuilder(world_1_1))
    publisher.tick_played(attempts)
    published = channel.read_all()[SLOT]
    assert [agent.faces_right for agent in published.agents] == [False, True]
    assert published.followed_world.mario.faces_right


def test_the_slot_carries_the_animation_frame_each_agent_shows(channel, world_1_1: StaticLevel):
    attempts = [Attempt(world_1_1, ends_on_stall=True) for _ in range(2)]
    for _ in range(TICKS_TO_MOVE_A_FEW_PIXELS):
        attempts[0].step(HOLD_NOTHING)
        attempts[1].step(HOLD_RIGHT)
    publisher = LiveChunkPublisher(channel.writer.open(), SLOT, GENERATION, FIRST_AGENT,
                                   ObservationBuilder(world_1_1))
    publisher.tick_played(attempts)
    published = channel.read_all()[SLOT]
    assert [agent.mario.pose for agent in published.agents] == [MarioPose.STANDING, MarioPose.WALKING]
    assert [agent.mario.walk_frame for agent in published.agents] == [
        attempt.mario.animation.walk_frame for attempt in attempts]


def test_a_newer_snapshot_replaces_the_older_one_in_its_slot(channel, world_1_1: StaticLevel):
    attempt = Attempt(world_1_1, ends_on_stall=True)
    publisher = LiveChunkPublisher(channel.writer.open(), SLOT, GENERATION, FIRST_AGENT, ObservationBuilder(world_1_1))
    for _ in range(3):
        attempt.step(HOLD_RIGHT)
        publisher.tick_played([attempt])
    assert channel.read_all()[SLOT].followed_world.tick == 3


def test_a_watched_chunk_plays_at_the_games_own_speed(channel, world_1_1: StaticLevel):
    attempt = Attempt(world_1_1, ends_on_stall=True)
    publisher = LiveChunkPublisher(channel.writer.open(), SLOT, GENERATION, FIRST_AGENT, ObservationBuilder(world_1_1))
    started_at = time.perf_counter()
    for _ in range(PACED_TICKS):
        attempt.step(HOLD_RIGHT)
        publisher.tick_played([attempt])
    seconds = time.perf_counter() - started_at
    assert seconds >= (PACED_TICKS - 1) / WATCHED_TICKS_PER_SECOND
    assert seconds < (PACED_TICKS + 15) / WATCHED_TICKS_PER_SECOND
