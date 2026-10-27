"""A block bumped from below, jumping up and falling back into place (the
original's bouncing block object: BumpBlock, BouncingBlockHandler)."""

from mario.constants.physics import (
    BLOCK_BOUNCE_GRAVITY,
    BLOCK_BOUNCE_SPEED,
    BLOCK_BOUNCE_TERMINAL_FALL_SPEED,
    SUBPIXEL_BITS,
)
from mario.simulation.gravity import add_gravity


class BouncingBlock:
    def __init__(self, column: int, row: int):
        self.column = column
        self.row = row
        self._offset_y = 0                       # sub-pixels from its place; negative is up
        self._velocity_y = BLOCK_BOUNCE_SPEED

    @property
    def offset_y_pixels(self) -> int:
        return self._offset_y >> SUBPIXEL_BITS

    @property
    def is_back_in_place(self) -> bool:
        return self._offset_y >= 0

    def step(self) -> None:
        self._offset_y += self._velocity_y
        self._velocity_y = add_gravity(self._velocity_y, BLOCK_BOUNCE_GRAVITY, BLOCK_BOUNCE_TERMINAL_FALL_SPEED)
