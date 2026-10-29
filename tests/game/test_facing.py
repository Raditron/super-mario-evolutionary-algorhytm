"""Which way Mario, an agent and an enemy face, as their snapshots carry it to the
Sprite view (#56): Mario the way he last held on the ground, an enemy the way it walks."""

from mario.level.static_level import StaticLevel
from mario.simulation.attempt import Attempt
from mario.simulation.attempt_tiles import AttemptTiles
from mario.simulation.goomba import Goomba
from mario.snapshots.world_snapshot import AgentSnapshot, EnemySnapshot, WorldSnapshot
from tests.game.helpers import HOLD_LEFT, HOLD_NOTHING, HOLD_RIGHT

TICKS_HELD = 10
# Long enough for the Goomba spawned against the pipe at columns 38-39 to turn at it.
TICKS_TO_TURN_AT_A_PIPE = 60


def test_mario_faces_right_at_the_start_left_once_left_is_held_and_right_again_once_right_is(flat_level):
    attempt = Attempt(flat_level)
    assert WorldSnapshot.of(attempt).mario.faces_right
    for _ in range(TICKS_HELD):
        attempt.step(HOLD_LEFT)
    assert not WorldSnapshot.of(attempt).mario.faces_right
    attempt.step(HOLD_NOTHING)
    assert not WorldSnapshot.of(attempt).mario.faces_right
    for _ in range(TICKS_HELD):
        attempt.step(HOLD_RIGHT)
    assert WorldSnapshot.of(attempt).mario.faces_right


def test_an_agent_faces_the_way_his_mario_does(flat_level):
    attempt = Attempt(flat_level)
    attempt.step(HOLD_LEFT)
    agent = AgentSnapshot.of(0, attempt)
    assert not agent.faces_right and not agent.mario.faces_right


def test_an_enemy_faces_left_as_it_spawns_walking_left_and_right_once_it_turns_at_a_wall(world_1_1: StaticLevel):
    goomba = Goomba(world_1_1.enemy_spawns[1])
    assert not EnemySnapshot.of(goomba).faces_right
    tiles = AttemptTiles(world_1_1)
    for tick in range(1, TICKS_TO_TURN_AT_A_PIPE + 1):
        goomba.step(tiles, tick)
    assert goomba.walks_right
    assert EnemySnapshot.of(goomba).faces_right
