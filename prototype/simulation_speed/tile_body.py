"""Axis-separated movement against the static tile map. PROTOTYPE.

Positions and velocities are integer sub-pixels, so every step is exact.
A body never moves more than one tile per tick, so checking the leading
edge after each axis move is enough.
"""

from . import constants as c

SHIFT = c.SUBPIXEL_TO_TILE_SHIFT


class TileBody:
    """A rectangle with integer sub-pixel position and velocity."""

    __slots__ = ("x", "y", "velocity_x", "velocity_y", "width", "height", "on_ground")

    def __init__(self, x_pixels: int, y_pixels: int, width_pixels: int, height_pixels: int):
        self.x = x_pixels * c.SUBPIXELS_PER_PIXEL
        self.y = y_pixels * c.SUBPIXELS_PER_PIXEL
        self.velocity_x = 0
        self.velocity_y = 0
        self.width = width_pixels * c.SUBPIXELS_PER_PIXEL
        self.height = height_pixels * c.SUBPIXELS_PER_PIXEL
        self.on_ground = False

    def move_horizontally(self, level) -> bool:
        """Apply velocity_x; returns True if a wall stopped the body."""
        if self.velocity_x == 0:
            return False
        self.x += self.velocity_x
        top_row = self.y >> SHIFT
        bottom_row = (self.y + self.height - 1) >> SHIFT
        if self.velocity_x > 0:
            edge_column = (self.x + self.width - 1) >> SHIFT
            if self._column_blocked(level, edge_column, top_row, bottom_row):
                self.x = edge_column * c.TILE_SIZE_SUBPIXELS - self.width
                return True
        else:
            edge_column = self.x >> SHIFT
            if self._column_blocked(level, edge_column, top_row, bottom_row):
                self.x = (edge_column + 1) * c.TILE_SIZE_SUBPIXELS
                return True
        return False

    def move_vertically(self, level) -> None:
        """Apply velocity_y, landing on or bumping into solid tiles."""
        self.y += self.velocity_y
        self.on_ground = False
        left_column = self.x >> SHIFT
        right_column = (self.x + self.width - 1) >> SHIFT
        if self.velocity_y > 0:
            edge_row = (self.y + self.height - 1) >> SHIFT
            if self._row_blocked(level, edge_row, left_column, right_column):
                self.y = edge_row * c.TILE_SIZE_SUBPIXELS - self.height
                self.velocity_y = 0
                self.on_ground = True
        elif self.velocity_y < 0:
            edge_row = self.y >> SHIFT
            if self._row_blocked(level, edge_row, left_column, right_column):
                self.y = (edge_row + 1) * c.TILE_SIZE_SUBPIXELS
                self.velocity_y = 0

    def overlaps(self, other: "TileBody") -> bool:
        return (self.x < other.x + other.width and other.x < self.x + self.width
                and self.y < other.y + other.height and other.y < self.y + self.height)

    @staticmethod
    def _column_blocked(level, column: int, top_row: int, bottom_row: int) -> bool:
        for row in range(top_row, bottom_row + 1):
            if level.is_solid(column, row):
                return True
        return False

    @staticmethod
    def _row_blocked(level, row: int, left_column: int, right_column: int) -> bool:
        for column in range(left_column, right_column + 1):
            if level.is_solid(column, row):
                return True
        return False
