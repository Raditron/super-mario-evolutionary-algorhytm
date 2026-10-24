"""The stall rule (training only): an attempt stalls once Mario has gone
STALL_LIMIT_TICKS ticks without a new furthest-right position.

Only a new furthest-right position resets the count, so pacing back and forth
behind it stalls as surely as standing still.
"""

from mario.constants.training import STALL_LIMIT_TICKS


class StallRule:
    def __init__(self, start_x_pixels: int):
        self._furthest_x_pixels = start_x_pixels
        self._ticks_without_progress = 0

    @property
    def has_stalled(self) -> bool:
        return self._ticks_without_progress >= STALL_LIMIT_TICKS

    def observe(self, x_pixels: int) -> None:
        """Mario's position after one tick."""
        if x_pixels > self._furthest_x_pixels:
            self._furthest_x_pixels = x_pixels
            self._ticks_without_progress = 0
        else:
            self._ticks_without_progress += 1
