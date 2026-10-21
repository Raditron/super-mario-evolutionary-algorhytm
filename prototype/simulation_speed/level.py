"""The shared, read-only World 1-1 tile map. PROTOTYPE.

One StaticLevel is loaded per process and shared by every agent: no agent ever
writes to it, so it costs nothing per agent.
"""

from pathlib import Path

import numpy as np

from . import constants as c


class StaticLevel:
    """Solid-tile lookup for World 1-1 plus the enemy spawn list."""

    def __init__(self, grid_rows: list[str]):
        self.width_tiles = len(grid_rows[0])
        self.height_tiles = len(grid_rows)
        # list of bytearrays: the fastest per-tile lookup from pure Python
        self.solid_rows = [bytearray(character in c.SOLID_TILE_CHARACTERS for character in row)
                           for row in grid_rows]
        self.flag_x_subpixels = c.FLAGPOLE_COLUMN * c.TILE_SIZE_SUBPIXELS
        self.bottom_y_subpixels = self.height_tiles * c.TILE_SIZE_SUBPIXELS
        self.observation_tiles = self._build_padded_observation_tiles()

    @classmethod
    def load_world_1_1(cls) -> "StaticLevel":
        level_path = Path(__file__).with_name(c.LEVEL_FILE_NAME)
        grid_rows = level_path.read_text().split()
        assert len(grid_rows) == c.LEVEL_HEIGHT_TILES
        assert all(len(row) == c.LEVEL_WIDTH_TILES for row in grid_rows)
        return cls(grid_rows)

    def is_solid(self, column: int, row: int) -> bool:
        if row < 0 or row >= self.height_tiles:
            return False                      # open sky above, pits below
        if column < 0 or column >= self.width_tiles:
            return True                       # level edges are walls
        return self.solid_rows[row][column] == 1

    def goomba_spawn_points_pixels(self) -> list[tuple[int, int]]:
        """(x, y) top-left spawn positions, in spawn (column) order."""
        spawn_points = [(column * c.TILE_SIZE_PIXELS, row * c.TILE_SIZE_PIXELS)
                        for column, row in c.SINGLE_GOOMBAS]
        ground_y = c.GROUND_ENEMY_ROW * c.TILE_SIZE_PIXELS
        for data_column in c.GOOMBA_PAIR_DATA_COLUMNS:
            first_x = (data_column - c.GOOMBA_PAIR_OFFSET_TILES) * c.TILE_SIZE_PIXELS
            spawn_points.append((first_x, ground_y))
            spawn_points.append((first_x + c.GOOMBA_PAIR_SPACING_PIXELS, ground_y))
        return sorted(spawn_points)

    def _build_padded_observation_tiles(self) -> np.ndarray:
        """Playfield rows as floats, padded left/right so any window slice is in range."""
        playfield = np.array(self.solid_rows[c.OBSERVATION_FIRST_ROW:], dtype=np.float64)
        playfield *= c.OBSERVATION_SOLID
        return np.pad(playfield,
                      ((0, 0), (c.OBSERVATION_COLUMNS_BEHIND, c.OBSERVATION_COLUMNS_AHEAD)),
                      constant_values=c.OBSERVATION_SOLID)
