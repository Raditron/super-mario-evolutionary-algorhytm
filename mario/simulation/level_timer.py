"""The level timer (the original's RunGameTimer): 400 units, one taken off every 24 ticks.

Reaching 0 ends the attempt.
"""

from mario.constants.level import LEVEL_TIMER_START_UNITS, LEVEL_TIMER_TICKS_PER_UNIT


class LevelTimer:
    def __init__(self):
        self.time_left = LEVEL_TIMER_START_UNITS
        self._ticks_into_unit = 0

    @property
    def has_run_out(self) -> bool:
        return self.time_left == 0

    def count_down(self) -> None:
        """One tick passes."""
        self._ticks_into_unit += 1
        if self._ticks_into_unit == LEVEL_TIMER_TICKS_PER_UNIT:
            self._ticks_into_unit = 0
            self.time_left -= 1
