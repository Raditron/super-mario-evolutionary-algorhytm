"""The warp pipe and the bonus room (#23, spec sections 1, 4 and 5): down on pipe
57 sinks Mario into the bonus room; its exit pipe brings him out of pipe 163.
Every timing is the original's (docs/research/world-1-1-layout.md, "The bonus room")."""

import copy
from dataclasses import replace

import numpy as np
import pytest

from mario.controller.controller_state import ControllerState
from mario.level.static_level import PipeDestination, StaticLevel
from mario.level.tile_kind import TileKind
from mario.simulation.area import Area
from mario.simulation.attempt import Attempt
from mario.simulation.attempt_result import EndReason, GameEvent, GameEventKind
from mario.simulation.observation_builder import ObservationBuilder
from tests.game.helpers import (
    HOLD_DOWN,
    HOLD_LEFT,
    HOLD_NOTHING,
    HOLD_RIGHT,
    HOLD_RIGHT_JUMP,
    WARP_PIPE_ENTRY_HITBOX_X_PIXELS,
    walk_onto_pipe,
    walk_onto_the_warp_pipe,
    without_enemies,
)

HOLD_LEFT_JUMP = ControllerState.bitmask(left=True, jump=True)
HOLD_DOWN_RIGHT = ControllerState.bitmask(down=True, right=True)
# ChangeAreaTimer = $30: Mario sinks 1 px a tick for 48 ticks, then the area changes.
SINKING_TICKS = 48
# In the room his sprite starts at PlayerStarting_X_Pos[1], PlayerStarting_Y_Pos[1],
# and he falls uncontrolled until its top is 48 px down (PlayerEntrance).
BONUS_ROOM_START_SPRITE = (0x18, 0x20)
BONUS_ROOM_CONTROL_SPRITE_Y_PIXELS = 0x30
# Long enough to see that nothing happens.
WATCHED_TICKS = 100


@pytest.fixture(scope="module")
def level(world_1_1: StaticLevel) -> StaticLevel:
    return without_enemies(world_1_1)


def on_the_warp_pipe(level: StaticLevel, hitbox_x_pixels: int = WARP_PIPE_ENTRY_HITBOX_X_PIXELS.start,
                     **attempt_options) -> Attempt:
    attempt = Attempt(level, **attempt_options)
    walk_onto_the_warp_pipe(attempt, hitbox_x_pixels)
    return attempt


def in_the_bonus_room(level: StaticLevel, **attempt_options) -> Attempt:
    """Just arrived: the sinking is over, the drop into the room not yet begun."""
    attempt = on_the_warp_pipe(level, **attempt_options)
    for _ in range(1 + SINKING_TICKS):
        attempt.step(HOLD_DOWN)
    return attempt


def sprite_of(attempt: Attempt) -> tuple[int, int]:
    return attempt.mario.sprite_x_pixels, attempt.mario.sprite_y_pixels


def ticks_of(attempt: Attempt, kind: GameEventKind) -> list[int]:
    return [event.tick for event in attempt.events if event.kind is kind]


def test_down_on_the_warp_pipe_enters_it(level):
    attempt = on_the_warp_pipe(level)
    attempt.step(HOLD_DOWN)
    assert GameEvent(attempt.ticks_elapsed, GameEventKind.ENTERED_PIPE) in attempt.events


@pytest.mark.parametrize("hitbox_x_pixels", [WARP_PIPE_ENTRY_HITBOX_X_PIXELS.start,
                                             WARP_PIPE_ENTRY_HITBOX_X_PIXELS.stop - 1])
def test_either_end_of_the_entry_window_enters(level, hitbox_x_pixels):
    attempt = on_the_warp_pipe(level, hitbox_x_pixels)
    attempt.step(HOLD_DOWN)
    assert ticks_of(attempt, GameEventKind.ENTERED_PIPE) == [attempt.ticks_elapsed]


def test_entering_mario_sinks_1_px_a_tick_for_48_ticks_whatever_is_pressed_then_is_in_the_bonus_room(level):
    attempt = on_the_warp_pipe(level)
    attempt.step(HOLD_DOWN)
    sprite_x, sprite_y = sprite_of(attempt)
    for tick in range(1, SINKING_TICKS):
        attempt.step(HOLD_LEFT_JUMP)
        assert (attempt.area, sprite_of(attempt)) == (Area.LEVEL, (sprite_x, sprite_y + tick))
    attempt.step(HOLD_LEFT_JUMP)
    assert attempt.area is Area.BONUS_ROOM
    assert sprite_of(attempt) == BONUS_ROOM_START_SPRITE


def test_in_the_bonus_room_mario_drops_uncontrolled_until_his_sprite_is_48_px_down(level):
    attempt = in_the_bonus_room(level)
    while attempt.mario.sprite_y_pixels < BONUS_ROOM_CONTROL_SPRITE_Y_PIXELS:
        attempt.step(HOLD_RIGHT)
        assert attempt.mario.velocity_x == 0
    attempt.step(HOLD_RIGHT)        # the original's PlayerRdy frame: nothing moves yet
    assert attempt.mario.velocity_x == 0
    attempt.step(HOLD_RIGHT)
    assert attempt.mario.velocity_x > 0


@pytest.mark.parametrize("hitbox_x_pixels", [WARP_PIPE_ENTRY_HITBOX_X_PIXELS.start - 1,
                                             WARP_PIPE_ENTRY_HITBOX_X_PIXELS.stop])
def test_with_a_foot_probe_off_the_pipes_top_down_does_not_enter(level, hitbox_x_pixels):
    attempt = on_the_warp_pipe(level, hitbox_x_pixels)
    for _ in range(WATCHED_TICKS):
        attempt.step(HOLD_DOWN)
    assert (attempt.area, ticks_of(attempt, GameEventKind.ENTERED_PIPE)) == (Area.LEVEL, [])


def test_down_with_left_or_right_held_does_not_enter(level):
    attempt = on_the_warp_pipe(level)
    attempt.step(HOLD_DOWN_RIGHT)
    assert ticks_of(attempt, GameEventKind.ENTERED_PIPE) == []


def test_entering_needs_mario_on_the_pipe_itself_not_just_down_on_the_ground(level):
    attempt = Attempt(level)
    for _ in range(WATCHED_TICKS):
        attempt.step(HOLD_DOWN)
    assert (attempt.area, ticks_of(attempt, GameEventKind.ENTERED_PIPE)) == (Area.LEVEL, [])


def test_no_pipe_but_the_one_leading_to_the_bonus_room_can_be_entered(level):
    """The same pipe 57, leading nowhere, is just a pipe."""
    pipe_leading_nowhere = replace(level.warp_pipe, leads_to=PipeDestination.NOTHING)
    level_without_a_warp_pipe = copy.copy(level)
    level_without_a_warp_pipe.pipes = tuple(pipe_leading_nowhere if pipe == level.warp_pipe else pipe
                                            for pipe in level.pipes)
    level_without_a_warp_pipe.warp_pipe = None
    attempt = Attempt(level_without_a_warp_pipe)
    walk_onto_pipe(attempt, pipe_leading_nowhere, WARP_PIPE_ENTRY_HITBOX_X_PIXELS.start)
    for _ in range(WATCHED_TICKS):
        attempt.step(HOLD_DOWN)
    assert (attempt.area, ticks_of(attempt, GameEventKind.ENTERED_PIPE)) == (Area.LEVEL, [])


# The room's exit pipe: its mouth's left edge, where the boxes stop Mario's right
# edge (sprite x 194, standing on the floor: sprite y 176).
EXIT_PIPE_TOUCH_SPRITE = (194, 176)
# AreaChangeTimerData on page 0: 160 ticks; he walks in at 0.5 px a tick until his
# sprite x is a multiple of 16 (208), 28 ticks, then stands.
EXIT_PIPE_WALK_TICKS = 160
EXIT_PIPE_WALK_TICKS_PER_PIXEL = 2
EXIT_PIPE_INSIDE_SPRITE_X = 208
# He comes out at page 10 (screen left 2560 px), his sprite at x 2560 + $38 and at
# y $f0, below the screen, and rises 1 px a tick until it is at y $90, on pipe
# 163's top (row 11): 96 ticks. His box is 2 px right of his sprite.
RETURN_SCREEN_LEFT_X_PIXELS = 2560
RETURN_START_SPRITE = (2616, 240)
SPRITE_TO_HITBOX_X_PIXELS = 2
RISING_TICKS = 96
PIPE_163_TOP_Y_PIXELS = 11 * 16
# Walking across the brick block, Mario's box touches the 7 coins over it (row 9,
# columns 4-10), 200 points each.
COIN_ROW_OVER_THE_BRICK_BLOCK = 9
COIN_COLUMNS_OVER_THE_BRICK_BLOCK = range(4, 11)
COIN_POINTS = 200
LEVEL_TIMER_TICKS_PER_UNIT = 24
STALL_LIMIT_TICKS = 180
# The Observation's window (spec section 7).
OBSERVATION_COLUMNS_BEHIND = 3
OBSERVATION_COLUMNS = 13
OBSERVATION_TOP_ROW = 2
OBSERVATION_ROWS = 12
# With Mario just dropped into the room (centre column 2), a brick of the block and
# a coin over it are in his window.
ROOM_BRICK_IN_THE_WINDOW = (4, 10)
ROOM_COIN_IN_THE_WINDOW = (4, 9)


def walk_into_the_exit_pipe(attempt: Attempt) -> None:
    """Hold right, jumping onto the brick block in the way, until Mario walks into
    the exit pipe's mouth: he can no longer be controlled."""
    jump_held_last_tick = False
    while attempt.is_mario_controlled:
        mario = attempt.mario
        if mario.is_on_ground:
            jump = not jump_held_last_tick and mario.is_flush_against_solid_tile_on_the_right(attempt.tiles)
        else:
            jump = jump_held_last_tick
        jump_held_last_tick = jump
        attempt.step(HOLD_RIGHT_JUMP if jump else HOLD_RIGHT)


def wait_for_control(attempt: Attempt) -> None:
    while not attempt.is_mario_controlled:
        attempt.step(HOLD_NOTHING)


def at_the_exit_pipe(level: StaticLevel, **attempt_options) -> Attempt:
    """Just touched the exit pipe's mouth."""
    attempt = in_the_bonus_room(level, **attempt_options)
    wait_for_control(attempt)
    walk_into_the_exit_pipe(attempt)
    return attempt


def out_of_the_bonus_room(level: StaticLevel) -> Attempt:
    """Just back in the level, below pipe 163, to rise out of it."""
    attempt = at_the_exit_pipe(level)
    for _ in range(EXIT_PIPE_WALK_TICKS):
        attempt.step(HOLD_LEFT)
    return attempt


def test_walking_into_the_exit_pipe_mario_walks_on_into_it_uncontrolled_for_160_ticks(level):
    attempt = at_the_exit_pipe(level)
    assert sprite_of(attempt) == EXIT_PIPE_TOUCH_SPRITE
    sprite_x, sprite_y = EXIT_PIPE_TOUCH_SPRITE
    for tick in range(1, EXIT_PIPE_WALK_TICKS):
        attempt.step(HOLD_LEFT_JUMP)
        expected_sprite_x = min(sprite_x + tick // EXIT_PIPE_WALK_TICKS_PER_PIXEL, EXIT_PIPE_INSIDE_SPRITE_X)
        assert (attempt.area, sprite_of(attempt)) == (Area.BONUS_ROOM, (expected_sprite_x, sprite_y))


def test_the_exit_pipe_puts_mario_below_pipe_163_with_the_screen_at_page_10(level):
    attempt = out_of_the_bonus_room(level)
    assert attempt.area is Area.LEVEL
    assert sprite_of(attempt) == RETURN_START_SPRITE
    assert attempt.scroll.left_x_pixels == RETURN_SCREEN_LEFT_X_PIXELS
    assert ticks_of(attempt, GameEventKind.EXITED_PIPE) == [attempt.ticks_elapsed]


def test_coming_out_mario_rises_1_px_a_tick_onto_pipe_163_then_is_controlled_again(level):
    attempt = out_of_the_bonus_room(level)
    sprite_x, sprite_y = RETURN_START_SPRITE
    for tick in range(1, RISING_TICKS + 1):
        assert not attempt.is_mario_controlled
        attempt.step(HOLD_LEFT_JUMP)
        assert sprite_of(attempt) == (sprite_x, sprite_y - tick)
    assert attempt.is_mario_controlled
    attempt.step(HOLD_LEFT)
    assert attempt.mario.is_on_ground and attempt.mario.hitbox().bottom_y_pixels == PIPE_163_TOP_Y_PIXELS
    assert attempt.mario.velocity_x < 0


def test_furthest_x_stays_at_the_warp_pipe_in_the_room_and_jumps_to_pipe_163_on_the_way_out(level):
    attempt = on_the_warp_pipe(level)
    furthest_x_on_the_warp_pipe = attempt.furthest_x
    attempt.step(HOLD_DOWN)
    wait_for_control(attempt)
    walk_into_the_exit_pipe(attempt)
    assert attempt.furthest_x == furthest_x_on_the_warp_pipe
    while attempt.area is Area.BONUS_ROOM:
        attempt.step(HOLD_NOTHING)
    assert attempt.furthest_x == RETURN_START_SPRITE[0] + SPRITE_TO_HITBOX_X_PIXELS


def test_coins_collected_in_the_room_count_and_score(level):
    """Every coin Mario's box touches leaves the room and counts: the 7 over the
    brick block he walks across, and any his jump onto it grazes."""
    attempt = in_the_bonus_room(level)
    score_before = attempt.scoreboard.score
    wait_for_control(attempt)
    walk_into_the_exit_pipe(attempt)
    room = level.bonus_room.tiles
    coins_gone = [(column, row) for column, row in room.coins if attempt.tiles.tile_kind(column, row) is TileKind.EMPTY]
    assert {(column, COIN_ROW_OVER_THE_BRICK_BLOCK) for column in COIN_COLUMNS_OVER_THE_BRICK_BLOCK} <= set(coins_gone)
    assert len(ticks_of(attempt, GameEventKind.COLLECTED_COIN)) == attempt.scoreboard.coins == len(coins_gone)
    assert attempt.scoreboard.score - score_before == len(coins_gone) * COIN_POINTS


def test_the_level_timer_stands_still_while_mario_cannot_be_controlled(level):
    """And each new area starts its first unit afresh: its first controlled tick takes one off."""
    attempt = on_the_warp_pipe(level)
    attempt.step(HOLD_DOWN)
    time_left = attempt.level_timer.time_left
    wait_for_control(attempt)
    assert attempt.level_timer.time_left == time_left
    attempt.step(HOLD_NOTHING)
    assert attempt.level_timer.time_left == time_left - 1
    for _ in range(LEVEL_TIMER_TICKS_PER_UNIT - 1):
        attempt.step(HOLD_NOTHING)
    assert attempt.level_timer.time_left == time_left - 1
    attempt.step(HOLD_NOTHING)
    assert attempt.level_timer.time_left == time_left - 2


def test_moving_right_in_the_room_counts_as_progress_though_it_is_left_of_the_warp_pipe(level):
    """The stall record starts again in each area."""
    attempt = in_the_bonus_room(level, ends_on_stall=True)
    wait_for_control(attempt)
    for _ in range(STALL_LIMIT_TICKS // 2):
        attempt.step(HOLD_NOTHING)
    for _ in range(STALL_LIMIT_TICKS // 2):
        attempt.step(HOLD_RIGHT)
    for _ in range(STALL_LIMIT_TICKS // 2):
        attempt.step(HOLD_NOTHING)
    assert not attempt.is_over


def test_standing_still_in_the_room_stalls_after_180_controlled_ticks(level):
    attempt = in_the_bonus_room(level, ends_on_stall=True)
    wait_for_control(attempt)
    for _ in range(STALL_LIMIT_TICKS - 1):
        attempt.step(HOLD_NOTHING)
    assert not attempt.is_over
    attempt.step(HOLD_NOTHING)
    assert attempt.end_reason is EndReason.STALLED


def tile_grid_around(attempt: Attempt, tiles: StaticLevel) -> np.ndarray:
    """The Observation's grid worked out from the spec one cell at a time: the 12
    rows from screen row 2, the 13 columns from 3 behind the one holding Mario's
    centre, solid +1 (outside the grid at the sides too), all else 0."""
    first_column = attempt.mario.centre_column - OBSERVATION_COLUMNS_BEHIND
    return np.array([[1.0 if tiles.is_solid(column, row) else 0.0
                      for column in range(first_column, first_column + OBSERVATION_COLUMNS)]
                     for row in range(OBSERVATION_TOP_ROW, OBSERVATION_TOP_ROW + OBSERVATION_ROWS)])


def test_in_the_bonus_room_the_observation_shows_the_rooms_tiles(level):
    """Built in one batch with an attempt still in the level, each sees its own area."""
    in_the_level = Attempt(level)
    in_the_room = in_the_bonus_room(level)
    wait_for_control(in_the_room)
    builder = ObservationBuilder(level)
    grids = builder.grid_of(builder.build_batch([in_the_level, in_the_room]))
    assert np.array_equal(grids[0], tile_grid_around(in_the_level, level))
    assert np.array_equal(grids[1], tile_grid_around(in_the_room, level.bonus_room.tiles))
    assert not np.array_equal(grids[0], grids[1])


def test_a_coin_shows_as_empty_and_a_broken_room_brick_as_empty_too(level):
    """Coins are not solid; the room's own changed tiles show as they now are."""
    attempt = in_the_bonus_room(level)
    wait_for_control(attempt)
    attempt.tiles.change_block(*ROOM_BRICK_IN_THE_WINDOW, TileKind.EMPTY)
    builder = ObservationBuilder(level)
    grid = builder.grid_of(builder.build(attempt))
    column, row = ROOM_BRICK_IN_THE_WINDOW
    first_column = attempt.mario.centre_column - OBSERVATION_COLUMNS_BEHIND
    assert grid[row - OBSERVATION_TOP_ROW, column - first_column] == 0
    assert grid[row - OBSERVATION_TOP_ROW, column + 1 - first_column] == 1
    coin_column, coin_row = ROOM_COIN_IN_THE_WINDOW
    assert grid[coin_row - OBSERVATION_TOP_ROW, coin_column - first_column] == 0


def ticks_until_it_stalls_standing_still(attempt: Attempt) -> int:
    """Worked out on a copy, which stands still until it stalls."""
    copy_of_attempt = copy.deepcopy(attempt)
    ticks = 0
    while not copy_of_attempt.is_over:
        copy_of_attempt.step(HOLD_NOTHING)
        ticks += 1
    assert copy_of_attempt.end_reason is EndReason.STALLED
    return ticks


def test_the_stall_count_stands_still_while_mario_cannot_be_controlled(level):
    """Standing on the warp pipe until a tick short of stalling, then going down,
    doesn't stall in the pipe; the room starts a new count."""
    attempt = on_the_warp_pipe(level, ends_on_stall=True)
    for _ in range(ticks_until_it_stalls_standing_still(attempt) - 2):
        attempt.step(HOLD_NOTHING)
    attempt.step(HOLD_DOWN)
    wait_for_control(attempt)
    assert not attempt.is_over
