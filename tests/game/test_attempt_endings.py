"""The level timer and the stall rule (#16, spec section 5)."""

from itertools import chain, cycle, repeat

from mario.constants.level import LEVEL_TIMER_START_UNITS
from mario.constants.training import STALL_LIMIT_TICKS
from mario.simulation.attempt import Attempt
from mario.simulation.attempt_result import EndReason
from tests.game.helpers import HOLD_LEFT, HOLD_NOTHING, HOLD_RIGHT

TIMER_RAN_OUT_TICK = 9600
TICKS_WITHOUT_ENDING = 2000


def standing_still():
    return repeat(HOLD_NOTHING)


def pacing_back_and_forth():
    """Walk right, then forever a little further left than right, against the screen's left edge."""
    return chain(repeat(HOLD_RIGHT, 40), cycle(chain(repeat(HOLD_LEFT, 45), repeat(HOLD_RIGHT, 35))))


def play_until_over(attempt: Attempt, buttons_per_tick, tick_limit: int) -> int:
    """Step until the attempt ends or the limit; return the tick of its last new furthest-right position."""
    last_new_furthest_x_tick = 0
    for buttons in buttons_per_tick:
        if attempt.is_over or attempt.ticks_elapsed == tick_limit:
            break
        furthest_x_before = attempt.furthest_x
        attempt.step(buttons)
        if attempt.furthest_x > furthest_x_before:
            last_new_furthest_x_tick = attempt.ticks_elapsed
    return last_new_furthest_x_tick


def test_the_level_timer_loses_one_unit_every_24_ticks(flat_level):
    attempt = Attempt(flat_level)
    play_until_over(attempt, standing_still(), 23)
    assert attempt.level_timer.time_left == LEVEL_TIMER_START_UNITS
    attempt.step(HOLD_NOTHING)
    assert attempt.level_timer.time_left == LEVEL_TIMER_START_UNITS - 1


def test_the_level_timer_ends_an_attempt_at_tick_9600(flat_level):
    attempt = Attempt(flat_level)
    play_until_over(attempt, standing_still(), TIMER_RAN_OUT_TICK - 1)
    assert not attempt.is_over
    attempt.step(HOLD_NOTHING)
    result = attempt.result()
    assert (result.end_reason, result.ticks_elapsed) == (EndReason.TIMER_RAN_OUT, TIMER_RAN_OUT_TICK)
    assert attempt.level_timer.time_left == 0


def test_with_the_stall_rule_standing_still_stalls_180_ticks_after_spawn(flat_level):
    attempt = Attempt(flat_level, ends_on_stall=True)
    play_until_over(attempt, standing_still(), TICKS_WITHOUT_ENDING)
    result = attempt.result()
    assert (result.end_reason, result.ticks_elapsed) == (EndReason.STALLED, STALL_LIMIT_TICKS)


def test_with_the_stall_rule_pacing_stalls_180_ticks_after_the_last_new_furthest_x(flat_level):
    attempt = Attempt(flat_level, ends_on_stall=True)
    last_new_furthest_x_tick = play_until_over(attempt, pacing_back_and_forth(), TICKS_WITHOUT_ENDING)
    result = attempt.result()
    assert result.end_reason is EndReason.STALLED
    assert result.ticks_elapsed == last_new_furthest_x_tick + STALL_LIMIT_TICKS
    assert last_new_furthest_x_tick > 0


def test_moving_right_keeps_resetting_the_stall_count(flat_level):
    attempt = Attempt(flat_level, ends_on_stall=True)
    play_until_over(attempt, repeat(HOLD_RIGHT), 2 * STALL_LIMIT_TICKS)
    assert not attempt.is_over


def test_without_the_stall_rule_standing_still_or_pacing_never_ends_the_attempt(flat_level):
    for buttons_per_tick in (standing_still(), pacing_back_and_forth()):
        attempt = Attempt(flat_level)
        play_until_over(attempt, buttons_per_tick, TICKS_WITHOUT_ENDING)
        assert not attempt.is_over
