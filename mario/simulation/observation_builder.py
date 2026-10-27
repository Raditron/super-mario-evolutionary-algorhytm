"""Builds Observations: what an agent perceives on one tick (spec section 7).

The grid's tiles never change during an Attempt, so the window for every
column Mario's centre can be in is worked out once per level. Building an
Observation is then one table lookup plus the enemies; a batch of them is one
numpy gather for the whole batch, which keeps training's hot path fast.
"""

import numpy as np

from mario.constants.observation import (
    EMPTY_CELL,
    ENEMY_CELL,
    OBSERVATION_BAND_TOP_Y,
    OBSERVATION_BOTTOM_ROW,
    OBSERVATION_COLUMNS,
    OBSERVATION_COLUMNS_BEHIND,
    OBSERVATION_GRID_CELLS,
    OBSERVATION_LENGTH,
    OBSERVATION_ROWS,
    OBSERVATION_STATE_DIVISORS,
    OBSERVATION_TOP_ROW,
    SOLID_CELL,
)
from mario.level.static_level import StaticLevel
from mario.level.tile_kind import INVISIBLE_SOLID_TILE_KINDS
from mario.simulation.attempt import Attempt
from mario.simulation.enemy import Enemy
from mario.simulation.mario import Mario


class ObservationBuilder:
    def __init__(self, level: StaticLevel):
        self._level_width_tiles = level.width_tiles
        self._grid_by_centre_column = _grids_by_centre_column(level)
        self._state_divisors = np.array(OBSERVATION_STATE_DIVISORS, dtype=np.float64)

    @staticmethod
    def grid_of(observations: np.ndarray) -> np.ndarray:
        """The grid of one Observation, or of each in a batch, as rows of cells from the
        top, each from left to right. A view: writing to it writes the Observations."""
        return observations[..., :OBSERVATION_GRID_CELLS].reshape(
            *observations.shape[:-1], OBSERVATION_ROWS, OBSERVATION_COLUMNS)

    @staticmethod
    def state_numbers_of(observations: np.ndarray) -> np.ndarray:
        """The four state numbers of one Observation, or of each in a batch. A view."""
        return observations[..., OBSERVATION_GRID_CELLS:]

    def build(self, attempt: Attempt) -> np.ndarray:
        """The attempt's Observation: a 1-D float64 vector."""
        return self.build_batch([attempt])[0]

    def build_with_first_column(self, attempt: Attempt) -> tuple[np.ndarray, int]:
        """The attempt's Observation, and the level column of its grid's leftmost cells."""
        centre_columns = self._centre_columns([attempt])
        return self._build([attempt], centre_columns)[0], _first_column(centre_columns[0])

    def build_batch(self, attempts: list[Attempt]) -> np.ndarray:
        """One Observation per attempt, as the rows of an (attempts x numbers) float64 array."""
        return self._build(attempts, self._centre_columns(attempts))

    def _centre_columns(self, attempts: list[Attempt]) -> list[int]:
        """The tile column holding each Mario's centre, which anchors his grid."""
        centre_columns = [attempt.mario.centre_column for attempt in attempts]
        # The solid columns either side keep Mario in the level, so this never fails;
        # it guards the gather in _build, where numpy would wrap a column of -1 round
        # to the level's right end. Two reductions per batch cost next to nothing.
        if centre_columns and (min(centre_columns) < 0 or max(centre_columns) >= self._level_width_tiles):
            raise ValueError(f"Mario's centre is outside the level, in columns {centre_columns}")
        return centre_columns

    def _build(self, attempts: list[Attempt], centre_columns: list[int]) -> np.ndarray:
        observations = np.empty((len(attempts), OBSERVATION_LENGTH), dtype=np.float64)
        grids = self.grid_of(observations)
        grids[...] = self._grid_by_centre_column[centre_columns]
        for grid, attempt, centre_column in zip(grids, attempts, centre_columns):
            _mark_enemies(grid, attempt.enemies.active, _first_column(centre_column))
        np.divide([_state_quantities(attempt.mario) for attempt in attempts], self._state_divisors,
                  out=self.state_numbers_of(observations))
        return observations


def _first_column(centre_column: int) -> int:
    return centre_column - OBSERVATION_COLUMNS_BEHIND


def _state_quantities(mario: Mario) -> tuple[int, int, int, int]:
    """Mario's state in the game's integer units, each to be divided by its divisor."""
    return mario.whole_speed_x, mario.velocity_y, mario.feet_y - OBSERVATION_BAND_TOP_Y, int(mario.is_on_ground)


def _mark_enemies(grid: np.ndarray, enemies: list[Enemy], first_column: int) -> None:
    """Each enemy marks the cell holding its hitbox centre, over whatever tile is there.
    A defeated one (a squashed Goomba) is no longer an enemy to avoid."""
    for enemy in enemies:
        if enemy.is_defeated:
            continue
        column_in_window = enemy.centre_column - first_column
        row_in_window = enemy.centre_row - OBSERVATION_TOP_ROW
        if 0 <= column_in_window < OBSERVATION_COLUMNS and 0 <= row_in_window < OBSERVATION_ROWS:
            grid[row_in_window, column_in_window] = ENEMY_CELL


def _grids_by_centre_column(level: StaticLevel) -> np.ndarray:
    """For every column Mario's centre can be in, the grid's tiles as rows of cells.
    A tile shows as solid when the physics treats it so and it can be seen; columns
    outside the level do too. The hidden 1-UP block isn't solid until hit, so it
    shows empty, and so does the invisible castle stopper."""
    grids = np.empty((level.width_tiles, OBSERVATION_ROWS, OBSERVATION_COLUMNS), dtype=np.float64)
    for centre_column in range(level.width_tiles):
        first_column = _first_column(centre_column)
        grids[centre_column] = [[SOLID_CELL if _shows_as_solid(level, column, row) else EMPTY_CELL
                                 for column in range(first_column, first_column + OBSERVATION_COLUMNS)]
                                for row in range(OBSERVATION_TOP_ROW, OBSERVATION_BOTTOM_ROW + 1)]
    return grids


def _shows_as_solid(level: StaticLevel, column: int, row: int) -> bool:
    return level.is_solid(column, row) and level.tile_kind(column, row) not in INVISIBLE_SOLID_TILE_KINDS
