"""What every item shares: a thing a block releases for Mario to collect (the
original's power-up object, an enemy object in slot 5).

It appears inside the block that released it and rises out of it, 1 px every
4 ticks (GrowThePowerUp), and then stays where it is; an item that moves on
from there says so itself (the mushrooms). Its position is the top-left corner
of its hitbox.
"""

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
from mario.simulation.attempt_result import GameEventKind
from mario.simulation.attempt_tiles import AttemptTiles
from mario.simulation.item_kind import ItemKind
from mario.simulation.tile_body import TileBody


class Item(TileBody):
    kind: ItemKind
    # The game event that collecting it reports.
    collected_event_kind: GameEventKind
    hitbox_offset_y_pixels = ITEM_HITBOX_OFFSET_Y_PIXELS

    def __init__(self, block_column: int, block_row: int):
        super().__init__(block_column * TILE_SIZE_SUBPIXELS, block_row * TILE_SIZE_SUBPIXELS,
                         ITEM_HITBOX_WIDTH_PIXELS * SUBPIXELS_PER_PIXEL,
                         ITEM_HITBOX_HEIGHT_PIXELS * SUBPIXELS_PER_PIXEL)
        self.is_emerging = True
        self._emerge_ticks = 0
        self._risen_pixels = 0

    @property
    def is_touchable(self) -> bool:
        """Whether Mario can collect it: once it has risen far enough out of its block."""
        return self._risen_pixels >= ITEM_TOUCHABLE_RISE_PIXELS

    def step(self, tiles: AttemptTiles) -> None:
        """Rise one pixel every few ticks; one step after the last pixel, it is out."""
        if not self.is_emerging:
            return
        self._emerge_ticks += 1
        if self._emerge_ticks % ITEM_EMERGE_TICKS_PER_PIXEL != 0:
            return
        if self._risen_pixels < ITEM_EMERGE_PIXELS:
            self.y -= SUBPIXELS_PER_PIXEL
            self._risen_pixels += 1
            return
        self.is_emerging = False
