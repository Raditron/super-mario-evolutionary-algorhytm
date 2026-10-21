"""What the stand-in brain sees: a 12 x 13 tile window around Mario. PROTOTYPE.

Solid tiles are 1, Goombas -1, empty 0. Only here to give the placeholder
brain a realistic per-tick input-building cost.
"""

import numpy as np

from . import constants as c

SHIFT = c.SUBPIXEL_TO_TILE_SHIFT
WINDOW_COLUMN_OFFSETS = np.arange(c.OBSERVATION_COLUMNS)


class TileGridObserver:
    def __init__(self, level):
        self.padded_tiles = level.observation_tiles       # shared, read-only
        self.last_column = level.width_tiles - 1

    def _mario_column(self, attempt) -> int:
        mario = attempt.mario
        column = (mario.x + (mario.width >> 1)) >> SHIFT
        return min(max(column, 0), self.last_column)

    def observe(self, attempt, observation: np.ndarray) -> None:
        """Fill one agent's observation vector (length OBSERVATION_SIZE) in place."""
        mario_column = self._mario_column(attempt)
        grid = observation.reshape(c.OBSERVATION_ROWS, c.OBSERVATION_COLUMNS)
        # padded index = column + COLUMNS_BEHIND, so the window starts at mario_column
        grid[:] = self.padded_tiles[:, mario_column:mario_column + c.OBSERVATION_COLUMNS]
        self._mark_goombas(attempt, mario_column, grid)

    def observe_many(self, attempts: list, observations: np.ndarray, rows: np.ndarray) -> None:
        """Fill observations[rows[i]] for attempts[i], with one vectorised gather."""
        mario_columns = np.fromiter((self._mario_column(attempt) for attempt in attempts),
                                    dtype=np.intp, count=len(attempts))
        windows = self.padded_tiles[:, mario_columns[:, None] + WINDOW_COLUMN_OFFSETS]
        grids = windows.transpose(1, 0, 2)                  # (agents, rows, columns)
        for index, attempt in enumerate(attempts):
            if attempt.active_goombas:
                self._mark_goombas(attempt, int(mario_columns[index]), grids[index])
        observations[rows] = grids.reshape(len(attempts), c.OBSERVATION_SIZE)

    @staticmethod
    def _mark_goombas(attempt, mario_column: int, grid: np.ndarray) -> None:
        first_column = mario_column - c.OBSERVATION_COLUMNS_BEHIND
        for goomba in attempt.active_goombas:
            column = ((goomba.x + (goomba.width >> 1)) >> SHIFT) - first_column
            row = ((goomba.y + (goomba.height >> 1)) >> SHIFT) - c.OBSERVATION_FIRST_ROW
            if 0 <= column < c.OBSERVATION_COLUMNS and 0 <= row < c.OBSERVATION_ROWS:
                grid[row, column] = c.OBSERVATION_ENEMY
