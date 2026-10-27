"""One Attempt's items: the item a block has released.

There is at most one, as in the original's single power-up slot (SetupPowerUp
uses enemy slot 5): a new one replaces the old. It is removed by the bounds
that remove an enemy, on either side of the screen, or once it falls into a pit
(OffscreenBoundsCheck).
"""

from mario.constants.level import (
    ENEMY_FELL_OUT_SPRITE_Y_PIXELS,
    ENEMY_REMOVAL_RANGE_PIXELS,
    SCREEN_RIGHT_EDGE_OFFSET_PIXELS,
)
from mario.simulation.attempt_tiles import AttemptTiles
from mario.simulation.fire_flower import FireFlower
from mario.simulation.hitbox import Hitbox
from mario.simulation.item import Item
from mario.simulation.item_kind import ItemKind
from mario.simulation.mushroom import Mushroom


class Items:
    def __init__(self):
        self._item: Item | None = None

    @property
    def active(self) -> list[Item]:
        return [] if self._item is None else [self._item]

    def release(self, kind: ItemKind, block_column: int, block_row: int) -> None:
        self._item = (FireFlower(block_column, block_row) if kind is ItemKind.FIRE_FLOWER
                      else Mushroom(kind, block_column, block_row))

    def step(self, tiles: AttemptTiles, screen_left_x_pixels: int) -> None:
        if self._item is None:
            return
        self._item.step(tiles)
        if _is_out_of_play(self._item, screen_left_x_pixels):
            self._item = None

    def take_touched(self, mario_hitbox: Hitbox) -> Item | None:
        """The item Mario is touching, which he collects: it leaves play."""
        item = self._item
        if item is None or not item.is_touchable or not item.hitbox().overlaps(mario_hitbox):
            return None
        self._item = None
        return item


def _is_out_of_play(item: Item, screen_left_x_pixels: int) -> bool:
    x_pixels = item.hitbox().x_pixels
    return (x_pixels < screen_left_x_pixels - ENEMY_REMOVAL_RANGE_PIXELS
            or x_pixels >= screen_left_x_pixels + SCREEN_RIGHT_EDGE_OFFSET_PIXELS + ENEMY_REMOVAL_RANGE_PIXELS
            or item.sprite_top_has_reached(ENEMY_FELL_OUT_SPRITE_Y_PIXELS))
