"""The stomp chain (the original's StompChainCounter and StompTimer).

Each stomp since Mario last landed climbs one step of the score table. A further
stomp on the same tick climbs one extra step and counts as a stomp even if Mario
is no longer falling (StompTimer is a frame timer, back at 0 on the next tick).
"""

from mario.constants.scoring import STOMP_CHAIN_POINTS


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
        return STOMP_CHAIN_POINTS[step - 1] if step <= len(STOMP_CHAIN_POINTS) else None
