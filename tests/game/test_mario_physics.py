"""Mario's movement against the #2 research values."""

import pytest

from mario.constants.physics import (
    AREA_ENTRY_FALLING_GRAVITY,
    HEAD_BUMP_SPEED,
    MARIO_TERMINAL_FALL_SPEED,
    RUN_SPEED_CAP,
    SLOW_JUMP_FALLING_GRAVITY,
    SUBPIXELS_PER_PIXEL,
    WALK_SPEED_CAP,
    X_SUBSPEED_MASK,
    Y_SUBSPEED_MASK,
)
from mario.constants.level import TILE_SIZE_SUBPIXELS
from mario.controller.controller_state import LEFT, RIGHT, ControllerState
from mario.simulation.mario import Mario, MovementState
from tests.game.helpers import (
    HOLD_JUMP,
    HOLD_LEFT,
    HOLD_NOTHING,
    HOLD_RIGHT,
    HOLD_RIGHT_RUN,
    build_level,
    step_mario,
)

TICKS_TO_REACH_ANY_CAP = 80
TICKS_TO_APEX_AND_BACK = 80
HOLD_RIGHT_RUN_JUMP = ControllerState.bitmask(right=True, run=True, jump=True)


def whole_speed_x(mario: Mario) -> int:
    return mario.velocity_x - (mario.velocity_x & X_SUBSPEED_MASK)


def jump_height_pixels(mario: Mario, level, buttons: int) -> float:
    takeoff_y = mario.y
    highest_y = mario.y
    for _ in range(TICKS_TO_APEX_AND_BACK):
        step_mario(mario, level, buttons)
        highest_y = min(highest_y, mario.y)
    return (takeoff_y - highest_y) / SUBPIXELS_PER_PIXEL


def test_holding_jump_from_standing_peaks_at_about_66_px(flat_level):
    assert jump_height_pixels(Mario(), flat_level, HOLD_JUMP) == pytest.approx(66, abs=1)


def test_holding_jump_from_a_run_peaks_at_about_82_px(flat_level):
    mario = Mario()
    step_mario(mario, flat_level, HOLD_RIGHT_RUN, TICKS_TO_REACH_ANY_CAP)
    assert jump_height_pixels(mario, flat_level, HOLD_RIGHT_RUN_JUMP) == pytest.approx(82.5, abs=1)


def test_tapping_jump_for_one_tick_gives_a_short_hop(flat_level):
    mario = Mario()
    step_mario(mario, flat_level, HOLD_JUMP)
    takeoff_height = (Mario().y - mario.y) / SUBPIXELS_PER_PIXEL
    assert takeoff_height + jump_height_pixels(mario, flat_level, HOLD_NOTHING) == pytest.approx(23, abs=1.5)


@pytest.mark.parametrize("buttons, speed_cap, pixels_per_16_ticks", [
    (HOLD_RIGHT, WALK_SPEED_CAP, 24),
    (HOLD_RIGHT_RUN, RUN_SPEED_CAP, 40),
])
def test_walk_and_run_caps_are_1_5_and_2_5_px_per_tick(flat_level, buttons, speed_cap, pixels_per_16_ticks):
    mario = Mario()
    step_mario(mario, flat_level, buttons, TICKS_TO_REACH_ANY_CAP)
    assert whole_speed_x(mario) == speed_cap
    start_x = mario.x
    step_mario(mario, flat_level, buttons, 16)
    assert (mario.x - start_x) // SUBPIXELS_PER_PIXEL == pixels_per_16_ticks


def test_releasing_run_keeps_the_run_cap_for_the_running_timer_then_clamps(flat_level):
    mario = Mario()
    step_mario(mario, flat_level, HOLD_RIGHT_RUN, TICKS_TO_REACH_ANY_CAP)
    speeds = []
    for _ in range(10):
        step_mario(mario, flat_level, HOLD_RIGHT)
        speeds.append(whole_speed_x(mario))
    assert speeds == [RUN_SPEED_CAP] * 9 + [WALK_SPEED_CAP]


def test_releasing_the_direction_slows_mario_to_a_stop(flat_level):
    mario = Mario()
    step_mario(mario, flat_level, HOLD_RIGHT_RUN, TICKS_TO_REACH_ANY_CAP)
    step_mario(mario, flat_level, HOLD_NOTHING, 60)
    assert whole_speed_x(mario) == 0


def test_a_skid_turns_mario_around(flat_level):
    mario = Mario()
    step_mario(mario, flat_level, HOLD_RIGHT_RUN, TICKS_TO_REACH_ANY_CAP)
    step_mario(mario, flat_level, HOLD_LEFT)
    assert (mario.facing_direction, mario.moving_direction) == (LEFT, RIGHT)
    step_mario(mario, flat_level, HOLD_LEFT, 40)
    assert mario.moving_direction == LEFT
    assert whole_speed_x(mario) < 0


def test_jumping_again_needs_a_fresh_press(flat_level):
    mario = Mario()
    step_mario(mario, flat_level, HOLD_JUMP, TICKS_TO_APEX_AND_BACK)
    assert mario.movement_state is MovementState.ON_GROUND
    step_mario(mario, flat_level, HOLD_JUMP, TICKS_TO_APEX_AND_BACK)
    assert mario.movement_state is MovementState.ON_GROUND
    step_mario(mario, flat_level, HOLD_NOTHING)
    step_mario(mario, flat_level, HOLD_JUMP)
    assert mario.movement_state is MovementState.JUMPING


@pytest.mark.parametrize("with_both_directions, alone", [
    (ControllerState.bitmask(left=True, right=True), HOLD_NOTHING),
    (ControllerState.bitmask(left=True, right=True, run=True), ControllerState.bitmask(run=True)),
    (ControllerState.bitmask(left=True, right=True, jump=True), HOLD_JUMP),
])
def test_holding_left_and_right_together_behaves_like_no_direction(flat_level, with_both_directions, alone):
    pressing_both, pressing_neither = Mario(), Mario()
    for mario, buttons in ((pressing_both, with_both_directions), (pressing_neither, alone)):
        step_mario(mario, flat_level, HOLD_RIGHT_RUN, 30)
        step_mario(mario, flat_level, buttons, 60)
    assert vars(pressing_both) == vars(pressing_neither)


def fall_speeds_after_walking_off_a_ledge(mario: Mario, level) -> list[int]:
    while mario.movement_state is MovementState.ON_GROUND:
        step_mario(mario, level, HOLD_RIGHT)
    speeds = []
    for _ in range(3):
        step_mario(mario, level, HOLD_RIGHT)
        speeds.append(mario.velocity_y)
    return speeds


def test_walking_off_a_ledge_before_any_jump_falls_with_the_area_entry_gravity():
    level = build_level(pit_columns=range(6, 40))
    gravity = AREA_ENTRY_FALLING_GRAVITY
    assert fall_speeds_after_walking_off_a_ledge(Mario(), level) == [gravity, 2 * gravity, 3 * gravity]


def test_walking_off_a_ledge_reuses_the_last_jumps_falling_gravity():
    level = build_level(pit_columns=range(6, 40))
    mario = Mario()
    step_mario(mario, level, HOLD_JUMP, TICKS_TO_APEX_AND_BACK)
    assert mario.movement_state is MovementState.ON_GROUND
    gravity = SLOW_JUMP_FALLING_GRAVITY
    assert fall_speeds_after_walking_off_a_ledge(mario, level) == [gravity, 2 * gravity, 3 * gravity]


def test_a_long_fall_overshoots_the_terminal_speed_for_a_tick_then_snaps_back():
    bottomless = build_level(pit_columns=range(0, 10))
    mario = Mario()
    fall_speeds = []
    for _ in range(60):
        step_mario(mario, bottomless, HOLD_NOTHING)
        fall_speeds.append(mario.velocity_y)
    fastest = max(fall_speeds)
    assert fastest / SUBPIXELS_PER_PIXEL == pytest.approx(4.5, abs=0.05)
    assert MARIO_TERMINAL_FALL_SPEED in fall_speeds[fall_speeds.index(fastest):]


def test_hitting_a_block_from_below_stops_the_rise():
    block_row = 9
    level = build_level(hard_blocks=frozenset({(2, block_row), (3, block_row)}))
    mario = Mario()
    step_mario(mario, level, HOLD_JUMP)
    while mario.velocity_y < 0:
        step_mario(mario, level, HOLD_JUMP)
    assert mario.y == (block_row + 1) * TILE_SIZE_SUBPIXELS
    assert mario.velocity_y - (mario.velocity_y & Y_SUBSPEED_MASK) == HEAD_BUMP_SPEED


def test_walls_stop_mario_and_his_speed():
    wall_column = 6
    level = build_level(hard_blocks=frozenset({(wall_column, 12)}))
    mario = Mario()
    step_mario(mario, level, HOLD_RIGHT_RUN, TICKS_TO_REACH_ANY_CAP)
    assert mario.x + mario.width == wall_column * TILE_SIZE_SUBPIXELS
    assert whole_speed_x(mario) == 0


def test_mario_lands_on_top_of_a_block():
    level = build_level(hard_blocks=frozenset({(5, 12)}))
    mario = Mario()
    step_mario(mario, level, ControllerState.bitmask(right=True, jump=True))
    while mario.movement_state is not MovementState.ON_GROUND:
        step_mario(mario, level, ControllerState.bitmask(right=True, jump=True))
    assert mario.y + mario.height == 12 * TILE_SIZE_SUBPIXELS
    assert mario.velocity_y == 0
