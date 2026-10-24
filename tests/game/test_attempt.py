import random

import pytest

from mario.constants.level import SCROLL_STOP_LEFT_X_PIXELS, SMALL_MARIO_HITBOX_OFFSET_X_PIXELS
from mario.constants.controller import CONTROLLER_BUTTONS
from mario.level.static_level import StaticLevel
from mario.simulation.attempt import Attempt
from mario.simulation.attempt_result import EndReason
from mario.snapshots.world_snapshot import VISIBLE_COLUMNS, WorldSnapshot
from tests.game.helpers import HOLD_LEFT, HOLD_RIGHT, HOLD_RIGHT_RUN, build_level
from tests.game.scripted_pilot import ScriptedPilot

CASTLE_STOPPER_COLUMN = 205
TICKS_TO_CROSS_THE_LEVEL = 3000


def attempt_state(attempt: Attempt) -> tuple:
    return (vars(attempt.mario), vars(attempt.scroll), attempt.ticks_elapsed,
            attempt.furthest_x, attempt.end_reason)


def sprite_screen_x(attempt: Attempt) -> int:
    return attempt.mario.pixel_x - SMALL_MARIO_HITBOX_OFFSET_X_PIXELS - attempt.scroll.left_x_pixels


def test_falling_into_a_pit_ends_the_attempt_with_the_furthest_x_reached():
    attempt = Attempt(build_level(pit_columns=range(10, 14)))
    rightmost_x = attempt.mario.pixel_x
    while not attempt.is_over:
        attempt.step(HOLD_RIGHT)
        rightmost_x = max(rightmost_x, attempt.mario.pixel_x)
    result = attempt.result()
    assert result.end_reason is EndReason.FELL_IN_PIT
    assert result.furthest_x == rightmost_x
    assert 10 * 16 - 12 < result.furthest_x < 14 * 16
    assert (result.final_score, result.coins_collected, result.events) == (0, 0, ())


def test_an_attempt_cannot_step_after_it_ends_or_report_before():
    attempt = Attempt(build_level(pit_columns=range(4, 10)))
    with pytest.raises(RuntimeError):
        attempt.result()
    while not attempt.is_over:
        attempt.step(HOLD_RIGHT)
    with pytest.raises(RuntimeError):
        attempt.step(HOLD_RIGHT)


def test_the_same_controller_log_gives_a_bit_identical_attempt(world_1_1):
    choices = random.Random(20261024)
    controller_log = [choices.randrange(1 << len(CONTROLLER_BUTTONS)) | HOLD_RIGHT for _ in range(1500)]
    first, second = Attempt(world_1_1), Attempt(StaticLevel.load_world_1_1())
    for attempt in (first, second):
        for buttons in controller_log:
            if attempt.is_over:
                break
            attempt.step(buttons)
    assert attempt_state(first) == attempt_state(second)


def test_mario_cannot_walk_off_the_screens_left_edge(world_1_1):
    attempt = Attempt(world_1_1)
    for buttons, ticks in ((HOLD_LEFT, 120), (HOLD_RIGHT_RUN, 200), (HOLD_LEFT, 300)):
        for _ in range(ticks):
            attempt.step(buttons)
            assert sprite_screen_x(attempt) >= 0
    assert sprite_screen_x(attempt) == 0


def test_the_pilot_crosses_1_1_and_the_screen_only_scrolls_right_until_column_192(world_1_1):
    attempt = Attempt(world_1_1)
    pilot = ScriptedPilot()
    scroll_positions = [attempt.scroll.left_x_pixels]
    for _ in range(TICKS_TO_CROSS_THE_LEVEL):
        attempt.step(pilot.next_buttons(attempt))
        assert not attempt.is_over
        scroll_positions.append(attempt.scroll.left_x_pixels)
    assert scroll_positions == sorted(scroll_positions)
    assert max(scroll_positions) == SCROLL_STOP_LEFT_X_PIXELS
    assert attempt.furthest_x >= CASTLE_STOPPER_COLUMN * 16 - 16


def test_a_snapshot_shows_the_screens_tiles_and_mario(world_1_1):
    attempt = Attempt(world_1_1)
    for _ in range(300):
        attempt.step(HOLD_RIGHT_RUN)
    snapshot = WorldSnapshot.of(attempt)
    assert snapshot.tick == 300
    assert snapshot.tiles.first_column == attempt.scroll.left_x_pixels // 16
    assert {len(row) for row in snapshot.tiles.rows} == {VISIBLE_COLUMNS}
    assert (snapshot.mario.x_pixels, snapshot.mario.y_pixels) == (attempt.mario.pixel_x, attempt.mario.pixel_y)
