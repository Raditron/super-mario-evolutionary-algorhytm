"""The score and coin counters and their game events (#16)."""

from mario.constants.scoring import COIN_POINTS
from mario.simulation.attempt import Attempt
from mario.simulation.attempt_result import GameEvent, GameEventKind
from tests.game.helpers import HOLD_NOTHING, build_level

STOMP_POINTS = 100


def test_points_are_counted_and_recorded_as_scored_points_with_the_amount(flat_level):
    attempt = Attempt(flat_level)
    attempt.step(HOLD_NOTHING)
    attempt.scoreboard.score_points(STOMP_POINTS, attempt.ticks_elapsed)
    assert attempt.scoreboard.score == STOMP_POINTS
    assert attempt.events == [GameEvent(1, GameEventKind.SCORED_POINTS, STOMP_POINTS)]


def test_a_coin_is_counted_recorded_and_worth_200_points(flat_level):
    attempt = Attempt(flat_level)
    attempt.scoreboard.collect_coin(attempt.ticks_elapsed)
    assert (attempt.scoreboard.coins, attempt.scoreboard.score) == (1, COIN_POINTS)
    assert attempt.events == [GameEvent(0, GameEventKind.COLLECTED_COIN),
                              GameEvent(0, GameEventKind.SCORED_POINTS, COIN_POINTS)]


def test_the_result_reports_the_score_coins_and_events():
    attempt = Attempt(build_level(pit_columns=range(0, 10)))
    attempt.scoreboard.collect_coin(attempt.ticks_elapsed)
    attempt.scoreboard.score_points(STOMP_POINTS, attempt.ticks_elapsed)
    while not attempt.is_over:
        attempt.step(HOLD_NOTHING)
    result = attempt.result()
    assert (result.final_score, result.coins_collected) == (COIN_POINTS + STOMP_POINTS, 1)
    assert result.events == tuple(attempt.events)
