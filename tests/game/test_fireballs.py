"""Fireballs: fire Mario throws them with the run button; they bounce along the
ground, vanish at walls and defeat the Goombas they hit (#20, spec sections 1 and 5)."""

import numpy as np
import pytest

from mario.controller.controller_state import ControllerState
from mario.level.static_level import EnemyKind, EnemySpawn
from mario.simulation.attempt import Attempt
from mario.simulation.attempt_result import DefeatMethod, GameEvent, GameEventKind
from mario.simulation.observation_builder import ObservationBuilder
from mario.snapshots.world_snapshot import FireballSnapshot, WorldSnapshot
from tests.game.helpers import (
    GROUND_TOP_ROW,
    HOLD_NOTHING,
    big_mario_attempt,
    build_level,
    fire_mario_attempt,
    goomba_spawn,
)

HOLD_RUN = ControllerState.bitmask(run=True)
HOLD_LEFT_RUN = ControllerState.bitmask(left=True, run=True)
HOLD_DOWN = ControllerState.bitmask(down=True)
HOLD_DOWN_RUN = ControllerState.bitmask(down=True, run=True)
TILE_PIXELS = 16
GROUND_Y = GROUND_TOP_ROW * TILE_PIXELS
WIDE_LEVEL_TILES = 60
# Fire Mario stands at the original's start: sprite x = 40, and his 32 px tall
# sprite's top 32 px above the ground's top (y = 208).
MARIO_SPRITE_X = 40
MARIO_SPRITE_Y = 176
# A fireball is an 8 x 8 box that starts at Mario's sprite x + 4 and his sprite y,
# then moves on the tick it is thrown: 4 px/f ahead and 4 px/f down
# (FireballObjCore, FireballXSpdData, BoundBoxCtrlData $07).
FIREBALL_SIZE = 8
FIREBALL_START_X = MARIO_SPRITE_X + 4
FIREBALL_SPEED = 4
FIREBALL_START_FALL_SPEED = 4
MARIO_ON_THE_GROUND_SPRITE_HEIGHT = 32
# It falls with gravity $50 / 256 px/f^2 up to 3 px/f; its 4 px/f start is clamped
# on the second tick (ImposeGravity). On the ground it bounces up at 3 px/f, which
# with that gravity rises just under 16 px (FireballBGCollision).
FIREBALL_TERMINAL_FALL_SPEED = 3
BOUNCE_PEAK_HEIGHTS = {15, 16}
FLIGHT_TICKS = 45
TICK_LIMIT = 200                  # ticks a test waits for something, at most
# A wall two tiles high a few columns right of Mario, as tall as the fireball bounces.
WALL_COLUMN = 9
WALL_X = WALL_COLUMN * TILE_PIXELS
# An exploding fireball stays where it exploded for 7 ticks, the last of which frees
# its slot (DrawExplosion_Fireball: state $80 counts up until $86).
EXPLOSION_TICKS = 7
FIREBALL_SLOTS = 2
# Run tapped every other tick for long enough to throw many, were there no limit;
# a fireball on open ground lives about 50 ticks.
TAPPING_TICKS = 40
# A fireball is removed once its x is at or left of the screen's left edge, 248 px
# or more right of it, or its y is 240 or more (GetFireballOffscreenBits, masked
# with %11001100). Thrown from x 44, it moves 4 px a tick: 244 is the last x it shows at.
LAST_X_BEFORE_THE_RIGHT_EDGE = 244
FELL_OUT_Y = 240
PIT_AHEAD = range(4, 12)
# A Goomba walking left at Mario from just past the screen's right edge.
GOOMBA_START_X = 260
# A Goomba that appears overlapping Mario's right side, behind his back as he
# throws left, so that it hurts him while his fireball still flies. Its turn in
# the spawn table comes with the screen's right edge, as a spawn on the screen
# would be skipped.
GOOMBA_OVER_MARIO = EnemySpawn(EnemyKind.GOOMBA, 46, GROUND_TOP_ROW - 1, 255)
# A Goomba hit by a fireball scores 100 (ShellOrBlockDefeat, GoombaPoints). It is
# lifted 2 px, then moves at 1 px/f away from Mario and rises at 3 px/f (SetStun),
# and falls through everything out of the level (MoveDefeatedEnemy).
GOOMBA_FIREBALL_POINTS = 100
KNOCKED_SPEED_X = 1
KNOCKED_SPEED_Y = -3


def fireballs_in(attempt: Attempt) -> tuple[FireballSnapshot, ...]:
    return WorldSnapshot.of(attempt).fireballs


def fireball_boxes(attempt: Attempt) -> list[tuple[int, int, int, int]]:
    return [(fireball.x_pixels, fireball.y_pixels, fireball.width_pixels, fireball.height_pixels)
            for fireball in fireballs_in(attempt)]


def step_while(attempt: Attempt, still_waiting) -> None:
    """Step with nothing held while still_waiting(), for at most TICK_LIMIT ticks."""
    for _ in range(TICK_LIMIT):
        if not still_waiting():
            return
        attempt.step(HOLD_NOTHING)


def event_kinds(attempt: Attempt) -> list[GameEventKind]:
    return [event.kind for event in attempt.events]


def shots(attempt: Attempt) -> int:
    return sum(event.kind is GameEventKind.SHOT_FIREBALL for event in attempt.events)


def test_fire_mario_pressing_run_throws_a_fireball_that_moves_on_the_tick_it_is_thrown():
    attempt = fire_mario_attempt(build_level())
    attempt.step(HOLD_RUN)
    assert attempt.events[-1] == GameEvent(attempt.ticks_elapsed, GameEventKind.SHOT_FIREBALL)
    assert fireball_boxes(attempt) == [(FIREBALL_START_X + FIREBALL_SPEED, MARIO_SPRITE_Y + FIREBALL_START_FALL_SPEED,
                                        FIREBALL_SIZE, FIREBALL_SIZE)]


def test_holding_run_throws_only_one_fireball_until_it_is_pressed_again():
    attempt = fire_mario_attempt(build_level())
    for _ in range(4):
        attempt.step(HOLD_RUN)
    assert shots(attempt) == 1
    attempt.step(HOLD_NOTHING)
    attempt.step(HOLD_RUN)
    assert shots(attempt) == 2


def test_big_mario_pressing_run_throws_nothing():
    attempt = big_mario_attempt(build_level())
    attempt.step(HOLD_RUN)
    assert fireballs_in(attempt) == () and shots(attempt) == 0


def throw_and_follow(attempt: Attempt, throw: int, ticks: int) -> list[tuple[int, int]]:
    """Throw one fireball, then its position each tick while it is in play."""
    attempt.step(throw)
    positions = [(fireballs_in(attempt)[0].x_pixels, fireballs_in(attempt)[0].y_pixels)]
    for _ in range(ticks):
        attempt.step(HOLD_NOTHING)
        if not fireballs_in(attempt):
            break
        positions.append((fireballs_in(attempt)[0].x_pixels, fireballs_in(attempt)[0].y_pixels))
    return positions


@pytest.mark.parametrize("throw, direction", [(HOLD_RUN, 1), (HOLD_LEFT_RUN, -1)])
def test_a_fireball_flies_at_4_pixels_a_tick_the_way_mario_faces(throw, direction):
    positions = throw_and_follow(fire_mario_attempt(build_level(width_tiles=WIDE_LEVEL_TILES)), throw, ticks=8)
    steps = [later[0] - earlier[0] for earlier, later in zip(positions, positions[1:])]
    assert len(steps) >= 4 and set(steps) == {direction * FIREBALL_SPEED}


def test_a_fireball_falls_to_the_ground_and_bounces_along_it():
    positions = throw_and_follow(fire_mario_attempt(build_level()), HOLD_RUN, ticks=FLIGHT_TICKS)
    heights = [GROUND_Y - (y + FIREBALL_SIZE) for _, y in positions]
    assert heights[:3] == [MARIO_ON_THE_GROUND_SPRITE_HEIGHT - FIREBALL_SIZE - FIREBALL_START_FALL_SPEED,
                           MARIO_ON_THE_GROUND_SPRITE_HEIGHT - FIREBALL_SIZE - 2 * FIREBALL_START_FALL_SPEED,
                           MARIO_ON_THE_GROUND_SPRITE_HEIGHT - FIREBALL_SIZE - 2 * FIREBALL_START_FALL_SPEED
                           - FIREBALL_TERMINAL_FALL_SPEED]
    assert min(heights) == 0
    landings = [index for index, height in enumerate(heights) if height == 0]
    assert len(landings) >= 2
    for landing, next_landing in zip(landings, landings[1:]):
        assert max(heights[landing:next_landing]) in BOUNCE_PEAK_HEIGHTS


def test_a_fireball_that_flies_into_a_wall_explodes_there_and_vanishes():
    level = build_level(hard_blocks=frozenset({(WALL_COLUMN, GROUND_TOP_ROW - 1), (WALL_COLUMN, GROUND_TOP_ROW - 2)}))
    attempt = fire_mario_attempt(level)
    attempt.step(HOLD_RUN)
    seen = []
    for _ in range(TICK_LIMIT):
        if not fireballs_in(attempt):
            break
        seen.append(fireballs_in(attempt)[0])
        attempt.step(HOLD_NOTHING)
    assert fireballs_in(attempt) == ()
    assert max(fireball.x_pixels for fireball in seen) < WALL_X + FIREBALL_SIZE  # less than its width in
    exploding = [fireball.is_exploding for fireball in seen]
    assert exploding[-EXPLOSION_TICKS:] == [True] * EXPLOSION_TICKS and not exploding[0]
    assert len({(fireball.x_pixels, fireball.y_pixels) for fireball in seen[-EXPLOSION_TICKS:]}) == 1


def test_never_more_than_two_fireballs_are_in_flight():
    """The original has two fireball slots; a press while both are busy throws nothing."""
    attempt = fire_mario_attempt(build_level())
    in_flight = []
    for tick in range(TAPPING_TICKS):
        attempt.step(HOLD_RUN if tick % 2 == 0 else HOLD_NOTHING)
        in_flight.append(len(fireballs_in(attempt)))
    assert max(in_flight) == FIREBALL_SLOTS
    assert shots(attempt) == FIREBALL_SLOTS


def test_once_a_fireball_has_gone_a_press_throws_another():
    attempt = fire_mario_attempt(build_level(hard_blocks=frozenset({(WALL_COLUMN, GROUND_TOP_ROW - 1),
                                                                    (WALL_COLUMN, GROUND_TOP_ROW - 2)})))
    in_flight = []
    for tick in range(TICK_LIMIT):
        attempt.step(HOLD_RUN if tick % 2 == 0 else HOLD_NOTHING)
        in_flight.append(len(fireballs_in(attempt)))
    assert shots(attempt) > FIREBALL_SLOTS
    assert max(in_flight) == FIREBALL_SLOTS


def last_seen_before_it_vanishes(attempt: Attempt, throw: int) -> FireballSnapshot:
    attempt.step(throw)
    last_seen = fireballs_in(attempt)[0]
    for _ in range(TICK_LIMIT):
        if not fireballs_in(attempt):
            break
        last_seen = fireballs_in(attempt)[0]
        attempt.step(HOLD_NOTHING)
    assert fireballs_in(attempt) == ()
    return last_seen


def test_a_fireball_vanishes_as_it_reaches_the_screens_right_edge():
    last_seen = last_seen_before_it_vanishes(fire_mario_attempt(build_level()), HOLD_RUN)
    assert last_seen.x_pixels == LAST_X_BEFORE_THE_RIGHT_EDGE and not last_seen.is_exploding


def test_a_fireball_vanishes_as_it_reaches_the_screens_left_edge():
    last_seen = last_seen_before_it_vanishes(fire_mario_attempt(build_level()), HOLD_LEFT_RUN)
    assert 0 < last_seen.x_pixels <= FIREBALL_SPEED


def test_a_fireball_that_falls_into_a_pit_vanishes_below_the_screen():
    last_seen = last_seen_before_it_vanishes(fire_mario_attempt(build_level(pit_columns=PIT_AHEAD)), HOLD_RUN)
    assert FELL_OUT_Y - FIREBALL_TERMINAL_FALL_SPEED <= last_seen.y_pixels < FELL_OUT_Y


def throw_at_a_goomba(attempt: Attempt) -> None:
    """Throw one fireball, and wait until it has defeated an enemy."""
    attempt.step(HOLD_RUN)
    step_while(attempt, lambda: GameEventKind.DEFEATED_ENEMY not in event_kinds(attempt))


def test_a_fireball_defeats_a_goomba_it_hits_for_100_points_and_explodes():
    attempt = fire_mario_attempt(build_level(enemy_spawns=(goomba_spawn(GOOMBA_START_X),)))
    throw_at_a_goomba(attempt)
    tick = attempt.ticks_elapsed
    assert attempt.events[-2:] == [GameEvent(tick, GameEventKind.DEFEATED_ENEMY, DefeatMethod.FIREBALL),
                                   GameEvent(tick, GameEventKind.SCORED_POINTS, GOOMBA_FIREBALL_POINTS)]
    assert [enemy.is_defeated for enemy in WorldSnapshot.of(attempt).enemies] == [True]
    assert [fireball.is_exploding for fireball in fireballs_in(attempt)] == [True]


def test_a_goomba_defeated_by_a_fireball_jumps_away_from_mario_and_falls_out_of_the_level():
    attempt = fire_mario_attempt(build_level(enemy_spawns=(goomba_spawn(GOOMBA_START_X),)))
    throw_at_a_goomba(attempt)
    hit = WorldSnapshot.of(attempt).enemies[0]
    attempt.step(HOLD_NOTHING)
    after = WorldSnapshot.of(attempt).enemies[0]
    assert (after.x_pixels - hit.x_pixels, after.y_pixels - hit.y_pixels) == (KNOCKED_SPEED_X, KNOCKED_SPEED_Y)
    step_while(attempt, lambda: WorldSnapshot.of(attempt).enemies)
    assert WorldSnapshot.of(attempt).enemies == () and not attempt.is_over


def test_when_fire_mario_is_hurt_his_fireballs_vanish():
    """Once he isn't fiery, ProcFireball_Bubble no longer runs his fireballs, nor draws them."""
    attempt = fire_mario_attempt(build_level(enemy_spawns=(GOOMBA_OVER_MARIO,)))
    attempt.step(HOLD_LEFT_RUN)
    fireballs_before_the_hurt = len(fireballs_in(attempt))
    for _ in range(TICK_LIMIT):
        if GameEventKind.TOOK_DAMAGE in event_kinds(attempt):
            break
        fireballs_before_the_hurt = len(fireballs_in(attempt))
        attempt.step(HOLD_NOTHING)
    assert GameEventKind.TOOK_DAMAGE in event_kinds(attempt)
    assert fireballs_before_the_hurt == 1 and fireballs_in(attempt) == ()


def test_crouching_fire_mario_throws_nothing():
    attempt = fire_mario_attempt(build_level())
    attempt.step(HOLD_DOWN)
    attempt.step(HOLD_DOWN_RUN)
    assert fireballs_in(attempt) == () and shots(attempt) == 0


def test_fireballs_are_not_shown_in_the_observation():
    """Spec section 7: Mario's fireballs aren't shown."""
    level = build_level()
    with_a_fireball, without = fire_mario_attempt(level), fire_mario_attempt(level)
    with_a_fireball.step(HOLD_RUN)
    without.step(HOLD_NOTHING)
    assert fireballs_in(with_a_fireball)
    builder = ObservationBuilder(level)
    assert np.array_equal(builder.build(with_a_fireball), builder.build(without))
