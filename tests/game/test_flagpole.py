"""The flagpole (#24, spec section 5): touching it ends a training attempt with
reached_flag and the original's flag-height and remaining-time points."""

import pytest

from mario.simulation.attempt import Attempt
from mario.simulation.attempt_result import EndReason, GameEvent, GameEventKind
from tests.game.helpers import GROUND_TOP_ROW, build_level
from tests.game.scripted_pilot import ScriptedPilot

FLAGPOLE_COLUMN = 40
FLAGPOLE_BALL_ROW = 2
FLAGPOLE_BASE_ROW = 12
STAIRCASE_FIRST_COLUMN = 12
TICK_LIMIT = 3000
# The original's remaining-time points (AwardGameTimerPoints): 50 a unit of the level timer.
POINTS_PER_TIME_UNIT_LEFT = 50


def flagpole_level(ledge_top_row: int):
    """Ground, a staircase of one-row steps up to a ledge whose top is the given
    row and which runs right up to the flagpole, as 1-1's ball, shaft and base block."""
    hard_blocks = set()
    staircase_height = FLAGPOLE_BASE_ROW + 1 - ledge_top_row
    for step in range(staircase_height):
        column = STAIRCASE_FIRST_COLUMN + step
        hard_blocks.update((column, row) for row in range(FLAGPOLE_BASE_ROW - step, GROUND_TOP_ROW))
    for column in range(STAIRCASE_FIRST_COLUMN + staircase_height, FLAGPOLE_COLUMN):
        hard_blocks.update((column, row) for row in range(ledge_top_row, GROUND_TOP_ROW))
    blocks = {(FLAGPOLE_COLUMN, FLAGPOLE_BALL_ROW): "o", (FLAGPOLE_COLUMN, FLAGPOLE_BASE_ROW): "#"}
    blocks.update({(FLAGPOLE_COLUMN, row): "|" for row in range(FLAGPOLE_BALL_ROW + 1, FLAGPOLE_BASE_ROW)})
    return build_level(hard_blocks=frozenset(hard_blocks), blocks=blocks)


def run_into_the_pole(attempt: Attempt) -> tuple[int, int]:
    """Run right, jumping up the steps, until the attempt ends; return the level
    timer's time left and the score on the tick before it ended."""
    pilot = ScriptedPilot()
    time_left_before = score_before = None
    while not attempt.is_over and attempt.ticks_elapsed < TICK_LIMIT:
        time_left_before, score_before = attempt.level_timer.time_left, attempt.scoreboard.score
        attempt.step(pilot.next_buttons(attempt))
    return time_left_before, score_before


def test_touching_the_pole_ends_a_training_attempt_with_reached_flag_and_the_height_and_time_points():
    attempt = Attempt(flagpole_level(ledge_top_row=7), ends_on_stall=True)
    time_left_at_the_touch, score_before_the_touch = run_into_the_pole(attempt)
    result = attempt.result()
    assert result.end_reason is EndReason.REACHED_FLAG
    assert attempt.level_timer.time_left == time_left_at_the_touch      # the timer stops at the touch
    time_points = POINTS_PER_TIME_UNIT_LEFT * time_left_at_the_touch
    assert result.events[-2:] == (GameEvent(result.ticks_elapsed, GameEventKind.SCORED_POINTS, 800),
                                  GameEvent(result.ticks_elapsed, GameEventKind.SCORED_POINTS, time_points))
    assert result.final_score == score_before_the_touch + 800 + time_points


# Walking along a ledge into the pole, small Mario's sprite's top is 32 px above
# the ledge's top: the original's bands (FlagpoleYPosData) start at sprite y 34, 80,
# 104 and 144, and the lower edges of the 800 and 100 bands are touched exactly.
@pytest.mark.parametrize("ledge_top_row, flag_points", [
    (4, 5000),      # sprite y 32
    (5, 2000),      # 48
    (7, 800),       # 80
    (8, 800),       # 96
    (9, 400),       # 112
    (11, 100),      # 144
])
def test_a_higher_touch_scores_more_points_in_the_original_bands(ledge_top_row, flag_points):
    attempt = Attempt(flagpole_level(ledge_top_row), ends_on_stall=True)
    run_into_the_pole(attempt)
    assert attempt.end_reason is EndReason.REACHED_FLAG
    assert attempt.flagpole_touch.flag_points == flag_points
