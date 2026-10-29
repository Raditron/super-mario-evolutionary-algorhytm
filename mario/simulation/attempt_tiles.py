"""One Attempt's tiles: the shared StaticLevel plus the blocks this Attempt has
changed, and the coins Mario has taken.

Mario and his enemies collide against these. They keep their own copy of the
level's solid-tile rows, so a lookup costs what it did against the StaticLevel;
outside the grid, the StaticLevel's rule answers.
"""

from mario.constants.level import TILE_SIZE_PIXELS
from mario.level.static_level import StaticLevel
from mario.level.tile_kind import SOLID_FROM_BELOW_ONLY_TILE_KINDS, SOLID_TILE_KINDS, TileKind
from mario.simulation.hitbox import Hitbox


class AttemptTiles:
    def __init__(self, level: StaticLevel):
        self.level = level
        self.width_tiles = level.width_tiles
        self.height_tiles = level.height_tiles
        self._solid_rows = [bytearray(row) for row in level.solid_rows]
        self._solid_from_below_rows = [bytearray(row) for row in level.solid_rows]
        for block in level.blocks:
            if block.kind in SOLID_FROM_BELOW_ONLY_TILE_KINDS:
                self._solid_from_below_rows[block.row][block.column] = True
        self.changed_blocks: dict[tuple[int, int], TileKind] = {}
        self._coins_left = set(level.coins)

    def take_coins_touched_by(self, hitbox: Hitbox) -> int:
        """The coins the box touches leave their tiles; how many there were."""
        if not self._coins_left:
            return 0
        touched_coins = self._coins_left.intersection(
            (column, row)
            for column in range(hitbox.x_pixels // TILE_SIZE_PIXELS, (hitbox.right_x_pixels - 1) // TILE_SIZE_PIXELS + 1)
            for row in range(hitbox.y_pixels // TILE_SIZE_PIXELS, (hitbox.bottom_y_pixels - 1) // TILE_SIZE_PIXELS + 1))
        for column, row in touched_coins:
            self._coins_left.remove((column, row))
            self.change_block(column, row, TileKind.EMPTY)
        return len(touched_coins)

    def tile_kind(self, column: int, row: int) -> TileKind:
        changed_kind = self.changed_blocks.get((column, row))
        return changed_kind if changed_kind is not None else self.level.tile_kind(column, row)

    def is_solid(self, column: int, row: int) -> bool:
        if 0 <= row < self.height_tiles and 0 <= column < self.width_tiles:
            return self._solid_rows[row][column] == 1
        return self.level.is_solid(column, row)

    def is_solid_from_below(self, column: int, row: int) -> bool:
        """Whether a head coming up from below is stopped here: a solid tile, or
        the hidden block before it is hit."""
        if 0 <= row < self.height_tiles and 0 <= column < self.width_tiles:
            return self._solid_from_below_rows[row][column] == 1
        return self.level.is_solid(column, row)

    def change_block(self, column: int, row: int, kind: TileKind) -> None:
        self.changed_blocks[column, row] = kind
        self._solid_rows[row][column] = kind in SOLID_TILE_KINDS
        self._solid_from_below_rows[row][column] = kind in SOLID_TILE_KINDS or kind in SOLID_FROM_BELOW_ONLY_TILE_KINDS
