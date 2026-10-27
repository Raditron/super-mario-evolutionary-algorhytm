"""Axis-separated box movement against an Attempt's solid tiles.

Positions are integer sub-pixels (1/4096 px). A body moves along one axis and
is pushed out of any solid tile it entered, then along the other. No body moves
more than one tile per tick, so checking its leading edge is enough.
"""

from enum import Enum, auto

from mario.constants.level import SUBPIXEL_TO_TILE_SHIFT, TILE_SIZE_SUBPIXELS
from mario.constants.physics import SUBPIXEL_BITS
from mario.simulation.attempt_tiles import AttemptTiles
from mario.simulation.hitbox import Hitbox


class VerticalContact(Enum):
    NONE = auto()
    LANDED = auto()
    HIT_CEILING = auto()


class TileBody:
    """A box with its top-left corner at (x, y) in sub-pixels."""

    # How far below the original's sprite position the hitbox starts.
    hitbox_offset_y_pixels: int

    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def hitbox(self) -> Hitbox:
        """The box in whole level pixels."""
        return Hitbox(self.x >> SUBPIXEL_BITS, self.y >> SUBPIXEL_BITS,
                      self.width >> SUBPIXEL_BITS, self.height >> SUBPIXEL_BITS)

    @property
    def feet_y(self) -> int:
        """The y just below the box: the top of whatever it stands on."""
        return self.y + self.height

    @property
    def centre_column(self) -> int:
        """The tile column holding the box's centre."""
        return (self.x + self.width // 2) >> SUBPIXEL_TO_TILE_SHIFT

    @property
    def centre_row(self) -> int:
        """The tile row holding the box's centre."""
        return (self.y + self.height // 2) >> SUBPIXEL_TO_TILE_SHIFT

    def sprite_top_has_reached(self, sprite_top_y_pixels: int) -> bool:
        """Whether the original's sprite has its top at this y or further down."""
        return (self.y >> SUBPIXEL_BITS) - self.hitbox_offset_y_pixels >= sprite_top_y_pixels

    def move_horizontally(self, tiles: AttemptTiles, distance: int) -> bool:
        """Move by distance; True if a solid tile stopped the body."""
        if distance == 0:
            return False
        self.x += distance
        top_row = self.y >> SUBPIXEL_TO_TILE_SHIFT
        bottom_row = (self.y + self.height - 1) >> SUBPIXEL_TO_TILE_SHIFT
        if distance > 0:
            leading_column = (self.x + self.width - 1) >> SUBPIXEL_TO_TILE_SHIFT
            if _column_has_solid_tile(tiles, leading_column, top_row, bottom_row):
                self.x = leading_column * TILE_SIZE_SUBPIXELS - self.width
                return True
        else:
            leading_column = self.x >> SUBPIXEL_TO_TILE_SHIFT
            if _column_has_solid_tile(tiles, leading_column, top_row, bottom_row):
                self.x = (leading_column + 1) * TILE_SIZE_SUBPIXELS
                return True
        return False

    def move_vertically(self, tiles: AttemptTiles, distance: int) -> VerticalContact:
        """Move by distance, landing on or bumping into solid tiles. Rising, the
        box can only hit a row it has just entered from below, which also stops it
        at a tile solid only from below (the hidden block)."""
        top_row_before = self.y >> SUBPIXEL_TO_TILE_SHIFT
        self.y += distance
        left_column = self.x >> SUBPIXEL_TO_TILE_SHIFT
        right_column = (self.x + self.width - 1) >> SUBPIXEL_TO_TILE_SHIFT
        if distance > 0:
            leading_row = (self.y + self.height - 1) >> SUBPIXEL_TO_TILE_SHIFT
            if _row_has_solid_tile(tiles, leading_row, left_column, right_column):
                self.y = leading_row * TILE_SIZE_SUBPIXELS - self.height
                return VerticalContact.LANDED
        elif distance < 0:
            leading_row = self.y >> SUBPIXEL_TO_TILE_SHIFT
            if leading_row < top_row_before and any(tiles.is_solid_from_below(column, leading_row)
                                                    for column in range(left_column, right_column + 1)):
                self.y = (leading_row + 1) * TILE_SIZE_SUBPIXELS
                return VerticalContact.HIT_CEILING
        return VerticalContact.NONE

    def overlaps_solid_tile(self, tiles: AttemptTiles) -> bool:
        """Whether the box is inside a solid tile, even in part."""
        left_column = self.x >> SUBPIXEL_TO_TILE_SHIFT
        right_column = (self.x + self.width - 1) >> SUBPIXEL_TO_TILE_SHIFT
        top_row = self.y >> SUBPIXEL_TO_TILE_SHIFT
        bottom_row = (self.y + self.height - 1) >> SUBPIXEL_TO_TILE_SHIFT
        return any(_row_has_solid_tile(tiles, row, left_column, right_column)
                   for row in range(top_row, bottom_row + 1))

    def is_standing_on_solid_tile(self, tiles: AttemptTiles) -> bool:
        row_below = self.feet_y >> SUBPIXEL_TO_TILE_SHIFT
        left_column = self.x >> SUBPIXEL_TO_TILE_SHIFT
        right_column = (self.x + self.width - 1) >> SUBPIXEL_TO_TILE_SHIFT
        return _row_has_solid_tile(tiles, row_below, left_column, right_column)


def _column_has_solid_tile(tiles: AttemptTiles, column: int, top_row: int, bottom_row: int) -> bool:
    return any(tiles.is_solid(column, row) for row in range(top_row, bottom_row + 1))


def _row_has_solid_tile(tiles: AttemptTiles, row: int, left_column: int, right_column: int) -> bool:
    return any(tiles.is_solid(column, row) for column in range(left_column, right_column + 1))
