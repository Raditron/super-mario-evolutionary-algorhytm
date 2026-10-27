"""The fire flower: an item that, once out of its block, stays where it is.

The original runs neither movement nor a background check for it
(PowerUpObjHandler skips both for power-up type 1), so nothing moves it.
"""

from mario.simulation.attempt_tiles import AttemptTiles
from mario.simulation.item import Item
from mario.simulation.item_kind import ItemKind


class FireFlower(Item):
    def __init__(self, block_column: int, block_row: int):
        super().__init__(ItemKind.FIRE_FLOWER, block_column, block_row)

    def hop_away_from(self, mario_x: int) -> None:
        """Its background check never runs, so a bumped block doesn't move it."""

    def _set_off(self) -> None:
        """It stays on its block."""

    def _move(self, tiles: AttemptTiles) -> None:
        """It doesn't move."""
