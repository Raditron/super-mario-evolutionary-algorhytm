"""A mushroom: the Super Mushroom or the 1-UP mushroom (the original's power-up object).

It appears inside the block that released it and rises out of it, 1 px every
4 ticks (GrowThePowerUp). Once out, it sets off right at 1 px/f and walks as an
enemy does: it turns at walls and falls off ledges (MoveNormalEnemy). Its
position is the top-left corner of its hitbox.
"""

from enum import StrEnum

from mario.constants.level import (
    MUSHROOM_HITBOX_HEIGHT_PIXELS,
    MUSHROOM_HITBOX_OFFSET_Y_PIXELS,
    MUSHROOM_HITBOX_WIDTH_PIXELS,
    TILE_SIZE_SUBPIXELS,
)
from mario.constants.physics import (
    MUSHROOM_SPEED,
    POWER_UP_EMERGE_PIXELS,
    POWER_UP_EMERGE_TICKS_PER_PIXEL,
    POWER_UP_TOUCHABLE_RISE_PIXELS,
    SUBPIXELS_PER_PIXEL,
)
from mario.simulation.attempt_tiles import AttemptTiles
from mario.simulation.walking_body import WalkingBody


class ItemKind(StrEnum):
    SUPER_MUSHROOM = "super_mushroom"
    ONE_UP_MUSHROOM = "one_up_mushroom"


class Mushroom(WalkingBody):
    hitbox_offset_y_pixels = MUSHROOM_HITBOX_OFFSET_Y_PIXELS

    def __init__(self, kind: ItemKind, block_column: int, block_row: int):
        super().__init__(block_column * TILE_SIZE_SUBPIXELS, block_row * TILE_SIZE_SUBPIXELS,
                         MUSHROOM_HITBOX_WIDTH_PIXELS * SUBPIXELS_PER_PIXEL,
                         MUSHROOM_HITBOX_HEIGHT_PIXELS * SUBPIXELS_PER_PIXEL,
                         velocity_x=0)
        self.kind = kind
        self.is_emerging = True
        self._emerge_ticks = 0
        self._risen_pixels = 0

    @property
    def is_touchable(self) -> bool:
        """Whether Mario can collect it: once it has risen far enough out of its block."""
        return self._risen_pixels >= POWER_UP_TOUCHABLE_RISE_PIXELS

    def step(self, tiles: AttemptTiles) -> None:
        if self.is_emerging:
            self._emerge()
        else:
            self.walk(tiles)

    def _emerge(self) -> None:
        """Rise one pixel every few ticks; one step after the last pixel, set off right."""
        self._emerge_ticks += 1
        if self._emerge_ticks % POWER_UP_EMERGE_TICKS_PER_PIXEL != 0:
            return
        if self._risen_pixels < POWER_UP_EMERGE_PIXELS:
            self.y -= SUBPIXELS_PER_PIXEL
            self._risen_pixels += 1
            return
        self.is_emerging = False
        self.is_falling = False
        self.velocity_x = MUSHROOM_SPEED
