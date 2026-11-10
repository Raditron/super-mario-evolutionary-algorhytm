"""Milestone 5: fitness rewards distance, coins and, only for a finisher, speed; reaching the flag always wins."""

import pytest

from mario.constants.level import LEVEL_TIMER_START_UNITS, LEVEL_TIMER_TICKS_PER_UNIT
from mario.simulation.attempt_result import AttemptResult, EndReason
from neuroevolution.algorithm_settings import AlgorithmSettings
from neuroevolution.fitness_function import FitnessFunction

# The plan's prices: a coin is worth 100 px of progress, which is 96 ticks of a finisher's time.
COIN_REWARD = 100
FLAG_REWARD = 20000
TICKS_PER_COIN = 96
TIME_REWARD = COIN_REWARD / TICKS_PER_COIN
FITNESS_SETTINGS = AlgorithmSettings.from_dict({
    "hidden_layer_size": 24,
    "button_press_threshold": 0.0,
    "coin_reward": COIN_REWARD,
    "flag_reward": FLAG_REWARD,
    "time_reward": TIME_REWARD,
    "tournament_size": 3,
    "mutation_rate": 0.05,
    "mutation_strength": 0.05,
    "crossover_rate": 0.7,
    "elite_count": 10,
})

# From the spawn to the flag is about this many pixels (the plan's figure).
FLAG_DISTANCE_PIXELS = 3170
SLOWEST_FINISH_TICKS = LEVEL_TIMER_START_UNITS * LEVEL_TIMER_TICKS_PER_UNIT
# Far more coins than the level holds, to give the best possible non-finisher every chance.
FAR_MORE_COINS_THAN_THE_LEVEL_HOLDS = 99
DEATH_DISTANCE_PIXELS = 500
SHORT_ATTEMPT_TICKS = 100
LONG_ATTEMPT_TICKS = 5000
NON_FINISHING_END_REASONS = [reason for reason in EndReason if reason is not EndReason.REACHED_FLAG]


def attempt(end_reason: EndReason, furthest_x: int, ticks_elapsed: int, coins_collected: int = 0) -> AttemptResult:
    return AttemptResult(
        end_reason=end_reason,
        furthest_x=furthest_x,
        ticks_elapsed=ticks_elapsed,
        final_score=0,
        coins_collected=coins_collected,
        events=(),
    )


def score(attempt_result: AttemptResult) -> float:
    return FitnessFunction(FITNESS_SETTINGS).score(attempt_result)


def test_the_score_is_a_float():
    assert isinstance(score(attempt(EndReason.DIED_TO_ENEMY, DEATH_DISTANCE_PIXELS, SHORT_ATTEMPT_TICKS)), float)


def test_more_distance_scores_higher():
    nearer = attempt(EndReason.DIED_TO_ENEMY, DEATH_DISTANCE_PIXELS, SHORT_ATTEMPT_TICKS)
    further = attempt(EndReason.DIED_TO_ENEMY, DEATH_DISTANCE_PIXELS + 1, SHORT_ATTEMPT_TICKS)

    assert score(further) > score(nearer)


def test_each_coin_adds_the_coin_reward():
    without_coins = attempt(EndReason.DIED_TO_ENEMY, DEATH_DISTANCE_PIXELS, SHORT_ATTEMPT_TICKS, coins_collected=0)
    with_three_coins = attempt(EndReason.DIED_TO_ENEMY, DEATH_DISTANCE_PIXELS, SHORT_ATTEMPT_TICKS, coins_collected=3)

    assert score(with_three_coins) - score(without_coins) == pytest.approx(3 * COIN_REWARD)


@pytest.mark.parametrize("end_reason", NON_FINISHING_END_REASONS)
def test_how_long_a_non_finisher_took_does_not_change_its_score(end_reason):
    quick = attempt(end_reason, DEATH_DISTANCE_PIXELS, SHORT_ATTEMPT_TICKS)
    slow = attempt(end_reason, DEATH_DISTANCE_PIXELS, LONG_ATTEMPT_TICKS)

    assert score(quick) == score(slow)


def test_a_faster_finisher_scores_higher():
    fast = attempt(EndReason.REACHED_FLAG, FLAG_DISTANCE_PIXELS, SHORT_ATTEMPT_TICKS)
    slow = attempt(EndReason.REACHED_FLAG, FLAG_DISTANCE_PIXELS, LONG_ATTEMPT_TICKS)

    assert score(fast) > score(slow)


def test_one_coin_is_worth_exactly_96_ticks_to_a_finisher():
    no_coin_quicker = attempt(EndReason.REACHED_FLAG, FLAG_DISTANCE_PIXELS, LONG_ATTEMPT_TICKS)
    one_coin_slower = attempt(EndReason.REACHED_FLAG, FLAG_DISTANCE_PIXELS, LONG_ATTEMPT_TICKS + TICKS_PER_COIN, coins_collected=1)

    assert score(one_coin_slower) == pytest.approx(score(no_coin_quicker))


def test_reaching_the_flag_beats_not_reaching_it_from_the_same_spot():
    died_at_the_flag = attempt(EndReason.DIED_TO_ENEMY, FLAG_DISTANCE_PIXELS, SHORT_ATTEMPT_TICKS)
    finished_slowly = attempt(EndReason.REACHED_FLAG, FLAG_DISTANCE_PIXELS, SLOWEST_FINISH_TICKS)

    assert score(finished_slowly) > score(died_at_the_flag)


def test_the_slowest_finisher_beats_the_best_possible_non_finisher():
    slowest_finisher = attempt(EndReason.REACHED_FLAG, FLAG_DISTANCE_PIXELS, SLOWEST_FINISH_TICKS)
    best_non_finisher = attempt(
        EndReason.TIMER_RAN_OUT, FLAG_DISTANCE_PIXELS, SLOWEST_FINISH_TICKS,
        coins_collected=FAR_MORE_COINS_THAN_THE_LEVEL_HOLDS,
    )

    assert score(slowest_finisher) > score(best_non_finisher)
