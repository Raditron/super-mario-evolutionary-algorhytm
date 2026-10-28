"""The stomp chain (the original's StompChainCounter and StompTimer).

Each stomp since Mario last landed climbs one step of the score table. A further
stomp on the same tick climbs one extra step and counts as a stomp even if Mario
is no longer falling (StompTimer is a frame timer, back at 0 on the next tick).
Kicking a shell scores from the same chain, without climbing it (HandlePECollisions).
"""

from mario.constants.scoring import (
    KICKED_SHELL_POINTS_BY_INTERVAL_TICKS_LEFT,
    KICKED_SHELL_STEPS_PAST_STOMP_CHAIN,
)
from mario.simulation.score_table import score_table_points


class StompChain:
    def __init__(self):
        self._stomps_since_landing = 0
        self._stomps_this_tick = 0

    @property
    def stomped_this_tick(self) -> bool:
        return self._stomps_this_tick > 0

    def start_tick(self) -> None:
        self._stomps_this_tick = 0

    def land(self) -> None:
        self._stomps_since_landing = 0

    def stomp(self) -> int | None:
        """One stomp; the points it scores, or None beyond the table (a 1-UP in the original)."""
        self._stomps_since_landing += 1
        step = self._stomps_since_landing + self._stomps_this_tick
        self._stomps_this_tick += 1
        return score_table_points(step)

    def kick_points(self, shell_interval_ticks_left: int) -> int | None:
        """What kicking a shell scores, given its interval timer: the chain's
        step 3 further, unless the shell is about to wake."""
        if shell_interval_ticks_left < len(KICKED_SHELL_POINTS_BY_INTERVAL_TICKS_LEFT):
            return KICKED_SHELL_POINTS_BY_INTERVAL_TICKS_LEFT[shell_interval_ticks_left]
        return score_table_points(self._stomps_since_landing + KICKED_SHELL_STEPS_PAST_STOMP_CHAIN)
