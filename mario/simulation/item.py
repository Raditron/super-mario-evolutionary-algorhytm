"""What every item shares: a thing a block releases for Mario to collect (the
original's power-up object, an enemy object in slot 5).

It appears inside the block that released it and rises out of it, 1 px every
4 ticks (GrowThePowerUp); then each kind of item does its own thing. Its
position is the top-left corner of its hitbox.
"""

from abc import ABC, abstractmethod

from mario.constants.level import (
    ITEM_HITBOX_HEIGHT_PIXELS,
    ITEM_HITBOX_OFFSET_Y_PIXELS,
    ITEM_HITBOX_WIDTH_PIXELS,
    TILE_SIZE_SUBPIXELS,
)
from mario.constants.physics import (
    ITEM_EMERGE_PIXELS,
    ITEM_EMERGE_TICKS_PER_PIXEL,
    ITEM_TOUCHABLE_RISE_PIXELS,
    SUBPIXELS_PER_PIXEL,
)
from mario.simulation.attempt_tiles import AttemptTiles
from mario.simulation.item_kind import ItemKind
from mario.simulation.walking_body import WalkingBody


class Item(WalkingBody, ABC):
    hitbox_offset_y_pixels = ITEM_HITBOX_OFFSET_Y_PIXELS

    def __init__(self, kind: ItemKind, block_column: int, block_row: int):
        super().__init__(block_column * TILE_SIZE_SUBPIXELS, block_row * TILE_SIZE_SUBPIXELS,
                         ITEM_HITBOX_WIDTH_PIXELS * SUBPIXELS_PER_PIXEL,
                         ITEM_HITBOX_HEIGHT_PIXELS * SUBPIXELS_PER_PIXEL,
                         velocity_x=0)
        self.kind = kind
        self.is_emerging = True
        self._emerge_ticks = 0
        self._risen_pixels = 0

    @property
    def is_touchable(self) -> bool:
        """Whether Mario can collect it: once it has risen far enough out of its block."""
        return self._risen_pixels >= ITEM_TOUCHABLE_RISE_PIXELS

    @abstractmethod
    def hop_away_from(self, mario_x: int) -> None:
        """The block under it was bumped from below."""

    def step(self, tiles: AttemptTiles) -> None:
        if self.is_emerging:
            self._emerge()
        else:
            self._move(tiles)

    @abstractmethod
    def _set_off(self) -> None:
        """It has risen out of its block."""

    @abstractmethod
    def _move(self, tiles: AttemptTiles) -> None:
        """One tick, once it is out of its block."""

    def _emerge(self) -> None:
        """Rise one pixel every few ticks; one step after the last pixel, it is out."""
        self._emerge_ticks += 1
        if self._emerge_ticks % ITEM_EMERGE_TICKS_PER_PIXEL != 0:
            return
        if self._risen_pixels < ITEM_EMERGE_PIXELS:
            self.y -= SUBPIXELS_PER_PIXEL
            self._risen_pixels += 1
            return
        self.is_emerging = False
        self._set_off()
