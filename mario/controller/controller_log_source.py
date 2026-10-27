"""Replay's Controller: the buttons a Controller log recorded, one tick after another."""

import numpy as np

from mario.controller.controller_source import ControllerSource


class ControllerLogSource(ControllerSource):
    def __init__(self, controller_log: np.ndarray):
        """controller_log: one uint8 Controller bitmask per tick of the attempt."""
        self._buttons_per_tick = controller_log.tolist()
        self._next_tick = 0

    def next_buttons(self) -> int:
        if self._next_tick == len(self._buttons_per_tick):
            raise IndexError("the Controller log has no more ticks")
        buttons = self._buttons_per_tick[self._next_tick]
        self._next_tick += 1
        return buttons
