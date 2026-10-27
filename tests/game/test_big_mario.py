"""Big Mario: he breaks bricks from below, crouches, and an enemy's touch makes him
small again instead of killing him (#19, spec sections 4, 5 and 6)."""

import pytest

from mario.constants.observation import EMPTY_CELL
from mario.constants.physics import SUBPIXELS_PER_PIXEL
from mario.controller.controller_state import ControllerState
from mario.level.tile_kind import TileKind
from mario.simulation.attempt import Attempt
from mario.simulation.attempt_result import DefeatMethod, EndReason, GameEvent, GameEventKind
from mario.simulation.mario import PowerState
from mario.simulation.observation_builder import ObservationBuilder
from mario.snapshots.world_snapshot import WorldSnapshot
from tests.game.helpers import (
    GROUND_TOP_ROW,
    HOLD_JUMP,
    HOLD_NOTHING,
    big_mario_attempt,
    build_level,
    goomba_spawn,
)

HOLD_DOWN = ControllerState.bitmask(down=True)
HOLD_DOWN_JUMP = ControllerState.bitmask(down=True, jump=True)
BRICK = "B"
COIN_QUESTION_BLOCK = "?"
MULTI_COIN_BRICK = "C"
STARMAN_BRICK = "S"
MARIO_SPAWN_COLUMN = 3
LOW_BLOCK_ROW = 9
TILE_PIXELS = 16
GROUND_Y = GROUND_TOP_ROW * TILE_PIXELS
TICK_LIMIT = 2000
BROKEN_BRICK_POINTS = 50                         # BrickShatter
BUMPED_ENEMY_POINTS = 100
# Breaking a brick sets Mario's Y speed byte to -2: he keeps rising (BrickShatter).
BRICK_BREAK_SPEED_PIXELS = -2
MARIO_WIDTH = 12
SMALL_MARIO_HEIGHT = 14
BIG_MARIO_HEIGHT = 28
# A brick platform over Mario's head with a Goomba walking left along it, from
# just past the screen's right edge. Big Mario's head reaches the low row about
# 6 ticks into a jump, while the Goomba walks 3 px.
BRICK_PLATFORM = {(column, LOW_BLOCK_ROW): BRICK for column in range(20)}
GOOMBA_ON_PLATFORM_X = 17 * TILE_PIXELS
GOOMBA_LEAD_PIXELS = 2
# A Goomba walking left at Mario from just past the screen's right edge, where it
# activates. Past him it turns at the level's left edge and comes back.
GOOMBA_START_X = 260
# Getting hurt freezes the game for 55 ticks (TimerControl from $FF down to $C8);
# then Mario can't be hurt for 8 interval ticks of 21 (InjuryTimer).
SHRINK_TICKS = 55
INVULNERABLE_TICKS_AFTER_SHRINKING = 8 * 21
# His size flips on the 15th frozen tick ($F0); then the animation alternates small
# and big, 4 ticks each, ten times (ChangeSizeOffsetAdder's last ten entries).
SHRINK_FLIP_TICK = 15
SHRINK_HEIGHTS_BY_TICK = ([BIG_MARIO_HEIGHT] * (SHRINK_FLIP_TICK - 1)
                          + [height for height in [SMALL_MARIO_HEIGHT, BIG_MARIO_HEIGHT] * 5 for _ in range(4)]
                          + [SMALL_MARIO_HEIGHT])


def event_kinds(attempt: Attempt) -> list[GameEventKind]:
    return [event.kind for event in attempt.events]


def jump_until_an_event(attempt: Attempt) -> None:
    attempt.step(HOLD_JUMP)
    while not attempt.events and attempt.mario.velocity_y < 0:
        attempt.step(HOLD_JUMP)


def jump_in_place(attempt: Attempt) -> None:
    attempt.step(HOLD_JUMP)
    while not attempt.mario.is_on_ground:
        attempt.step(HOLD_JUMP)
    attempt.step(HOLD_NOTHING)


def tile_kind_in_snapshot(attempt: Attempt, column: int, row: int) -> TileKind:
    tiles = WorldSnapshot.of(attempt).tiles
    return tiles.rows[row][column - tiles.first_column]


def mario_box(attempt: Attempt) -> tuple[int, int, int, int]:
    mario = WorldSnapshot.of(attempt).mario
    return mario.x_pixels, mario.y_pixels, mario.width_pixels, mario.height_pixels


def test_big_mario_breaks_a_brick_from_below_and_keeps_rising():
    attempt = big_mario_attempt(build_level(blocks={(MARIO_SPAWN_COLUMN, LOW_BLOCK_ROW): BRICK}))
    jump_until_an_event(attempt)
    tick = attempt.ticks_elapsed
    assert attempt.events == [GameEvent(tick, GameEventKind.BROKE_BRICK),
                              GameEvent(tick, GameEventKind.SCORED_POINTS, BROKEN_BRICK_POINTS)]
    assert attempt.mario.velocity_y // SUBPIXELS_PER_PIXEL == BRICK_BREAK_SPEED_PIXELS


def test_a_broken_brick_shows_as_empty_in_the_snapshot_and_the_observation():
    level = build_level(blocks={(MARIO_SPAWN_COLUMN, LOW_BLOCK_ROW): BRICK})
    attempt = big_mario_attempt(level)
    jump_until_an_event(attempt)
    assert tile_kind_in_snapshot(attempt, MARIO_SPAWN_COLUMN, LOW_BLOCK_ROW) is TileKind.EMPTY
    observation, first_column = ObservationBuilder(level).build_with_first_column(attempt)
    grid = ObservationBuilder.grid_of(observation)
    observation_top_row = 2
    assert grid[LOW_BLOCK_ROW - observation_top_row, MARIO_SPAWN_COLUMN - first_column] == EMPTY_CELL


def test_big_mario_rises_on_into_where_the_brick_was():
    attempt = big_mario_attempt(build_level(blocks={(MARIO_SPAWN_COLUMN, LOW_BLOCK_ROW): BRICK}))
    jump_until_an_event(attempt)
    brick_bottom_y = (LOW_BLOCK_ROW + 1) * TILE_PIXELS
    assert attempt.mario.hitbox().y_pixels == brick_bottom_y
    attempt.step(HOLD_JUMP)
    assert attempt.mario.hitbox().y_pixels < brick_bottom_y


@pytest.mark.parametrize("block", [COIN_QUESTION_BLOCK, MULTI_COIN_BRICK, STARMAN_BRICK])
def test_big_mario_only_bumps_a_block_with_something_in_it(block):
    attempt = big_mario_attempt(build_level(blocks={(MARIO_SPAWN_COLUMN, LOW_BLOCK_ROW): block}))
    jump_in_place(attempt)
    assert GameEventKind.BROKE_BRICK not in event_kinds(attempt)
    assert tile_kind_in_snapshot(attempt, MARIO_SPAWN_COLUMN, LOW_BLOCK_ROW) is not TileKind.EMPTY


def goomba_centre_x(attempt: Attempt) -> int:
    hitbox = attempt.enemies.active[0].hitbox()
    return hitbox.x_pixels + hitbox.width_pixels // 2


def test_a_goomba_standing_on_a_brick_big_mario_breaks_is_defeated():
    attempt = big_mario_attempt(build_level(blocks=BRICK_PLATFORM,
                                            enemy_spawns=(goomba_spawn(GOOMBA_ON_PLATFORM_X, LOW_BLOCK_ROW - 1),)))
    jump_at_x = (MARIO_SPAWN_COLUMN + 1) * TILE_PIXELS + GOOMBA_LEAD_PIXELS
    while not attempt.enemies.active or goomba_centre_x(attempt) > jump_at_x:
        attempt.step(HOLD_NOTHING)
    jump_until_an_event(attempt)
    tick = attempt.ticks_elapsed
    assert attempt.events == [GameEvent(tick, GameEventKind.BROKE_BRICK),
                              GameEvent(tick, GameEventKind.SCORED_POINTS, BROKEN_BRICK_POINTS),
                              GameEvent(tick, GameEventKind.DEFEATED_ENEMY, DefeatMethod.BUMPED),
                              GameEvent(tick, GameEventKind.SCORED_POINTS, BUMPED_ENEMY_POINTS)]


def test_big_mario_crouches_with_down_on_the_ground_into_small_marios_box():
    attempt = big_mario_attempt(build_level())
    x, _, _, _ = mario_box(attempt)
    attempt.step(HOLD_DOWN)
    assert mario_box(attempt) == (x, GROUND_Y - SMALL_MARIO_HEIGHT, MARIO_WIDTH, SMALL_MARIO_HEIGHT)
    attempt.step(HOLD_NOTHING)
    assert mario_box(attempt) == (x, GROUND_Y - BIG_MARIO_HEIGHT, MARIO_WIDTH, BIG_MARIO_HEIGHT)


def test_a_crouch_jump_stays_crouched_in_the_air_even_once_down_is_let_go():
    attempt = big_mario_attempt(build_level())
    attempt.step(HOLD_DOWN)
    attempt.step(HOLD_DOWN_JUMP)
    attempt.step(HOLD_JUMP)
    assert not attempt.mario.is_on_ground
    assert mario_box(attempt)[3] == SMALL_MARIO_HEIGHT


def touches_an_enemy(attempt: Attempt) -> bool:
    mario = attempt.mario.hitbox()
    return any(enemy.hitbox().overlaps(mario) for enemy in attempt.enemies.active)


def wait_until_hurt(attempt: Attempt) -> None:
    while GameEventKind.TOOK_DAMAGE not in event_kinds(attempt) and not attempt.is_over:
        attempt.step(HOLD_NOTHING)


def test_big_mario_touched_by_a_goomba_becomes_small_and_survives():
    attempt = big_mario_attempt(build_level(enemy_spawns=(goomba_spawn(GOOMBA_START_X),)))
    wait_until_hurt(attempt)
    tick = attempt.ticks_elapsed
    assert attempt.events == [GameEvent(tick, GameEventKind.TOOK_DAMAGE)]
    assert WorldSnapshot.of(attempt).mario.power_state is PowerState.SMALL
    for _ in range(SHRINK_TICKS):
        attempt.step(HOLD_NOTHING)
    assert not attempt.is_over
    assert mario_box(attempt)[2:] == (MARIO_WIDTH, SMALL_MARIO_HEIGHT)


def test_while_mario_shrinks_the_game_stands_still_and_his_box_follows_the_shrink_animation():
    attempt = big_mario_attempt(build_level(enemy_spawns=(goomba_spawn(GOOMBA_START_X),)))
    wait_until_hurt(attempt)
    goomba_x = attempt.enemies.active[0].hitbox().x_pixels
    heights = []
    for _ in range(SHRINK_TICKS):
        attempt.step(HOLD_NOTHING)
        heights.append(mario_box(attempt)[3])
    assert heights == SHRINK_HEIGHTS_BY_TICK
    assert attempt.enemies.active[0].hitbox().x_pixels == goomba_x


def test_during_the_invulnerability_a_second_touch_does_nothing_but_one_after_it_kills():
    attempt = big_mario_attempt(build_level(enemy_spawns=(goomba_spawn(GOOMBA_START_X),)))
    wait_until_hurt(attempt)
    hurt_tick = attempt.ticks_elapsed
    touching_ticks = 0
    while WorldSnapshot.of(attempt).mario.is_invulnerable:
        attempt.step(HOLD_NOTHING)
        touching_ticks += touches_an_enemy(attempt)
    assert attempt.ticks_elapsed - hurt_tick == SHRINK_TICKS + INVULNERABLE_TICKS_AFTER_SHRINKING
    assert touching_ticks > 0 and not attempt.is_over
    while not attempt.is_over and attempt.ticks_elapsed < TICK_LIMIT:
        attempt.step(HOLD_NOTHING)
    assert attempt.result().end_reason is EndReason.DIED_TO_ENEMY
    assert event_kinds(attempt) == [GameEventKind.TOOK_DAMAGE]
