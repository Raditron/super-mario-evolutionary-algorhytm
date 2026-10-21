"""Replay checks: rebuild attempts from recorded Controller buttons alone. PROTOTYPE."""

from .attempt import Attempt


def replay_attempt(level, controller_log: bytes) -> Attempt:
    """Re-simulate an attempt from its Controller log; no brain involved."""
    attempt = Attempt(level)
    for buttons in controller_log:
        attempt.step(buttons)
    return attempt


class ReplayVerifier:
    def __init__(self, level):
        self.level = level

    def count_replay_mismatches(self, results) -> int:
        """How many attempts do NOT end bit-identical when replayed from their logs."""
        mismatches = 0
        for result in results:
            replayed = replay_attempt(self.level, result.controller_log)
            if not (replayed.is_over and replayed.tick == result.ticks
                    and replayed.state_digest() == result.final_state_digest):
                mismatches += 1
        return mismatches

    @staticmethod
    def count_differing_attempts(first_results, second_results) -> int:
        """How many agents pressed different buttons or ended differently in two runs."""
        return sum(first.controller_log != second.controller_log
                   or first.final_state_digest != second.final_state_digest
                   for first, second in zip(first_results, second_results, strict=True))
