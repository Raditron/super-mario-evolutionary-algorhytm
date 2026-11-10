"""Milestone 5: the score that decides which agents get to pass their genome on."""

from mario.simulation.attempt_result import AttemptResult, EndReason
from neuroevolution.algorithm_settings import AlgorithmSettings


class FitnessFunction:
    """fitness = furthest_x + coin_reward * coins, and for an agent that reached the flag also flag_reward - time_reward * ticks.

    Time only counts for agents that reached the flag: otherwise "fewer ticks is better" would reward dying fast.
    """

    def __init__(self, settings: AlgorithmSettings) -> None:
        self._settings = settings

    def finish_bonus(self, attempt_result: AttemptResult) -> float:
        """The flag reward minus the time used, for an agent that reached the flag; 0 for everyone else."""
        if attempt_result.end_reason == EndReason.REACHED_FLAG:
            return (
                self._settings.flag_reward
                - self._settings.time_reward * attempt_result.ticks_elapsed
            )
        return 0.0

    def score(self, attempt_result: AttemptResult) -> float:
        """The fitness one agent earns for its attempt."""
        return float(
            attempt_result.furthest_x
            + self._settings.coin_reward * attempt_result.coins_collected
            + self.finish_bonus(attempt_result)
        )
