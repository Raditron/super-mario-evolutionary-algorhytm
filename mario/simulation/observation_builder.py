"""Builds Observations: what an agent perceives on one tick (spec section 7).

The grid's tiles never change during an Attempt, so the window for every
column Mario's centre can be in is worked out once per level. Building an
Observation is then one table lookup plus the enemies; a batch of them is one
numpy gather for the whole batch, which keeps training's hot path fast.
"""

import numpy as np

from mario.constants.level import SUBPIXEL_TO_TILE_SHIFT
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
from mario.simulation.tile_body import TileBody


class ObservationBuilder:
    def __init__(self, level: StaticLevel):
        self._grid_by_centre_column = _grids_by_centre_column(level)
        self._state_divisors = np.array(OBSERVATION_STATE_DIVISORS, dtype=np.float64)

    @staticmethod
    def window_first_column(attempt: Attempt) -> int:
        """The level column of the grid's leftmost cells."""
        return _centre_column(attempt.mario) - OBSERVATION_COLUMNS_BEHIND

    def build(self, attempt: Attempt) -> np.ndarray:
        """The attempt's Observation: a 1-D float64 vector."""
        return self.build_batch([attempt])[0]

    def build_batch(self, attempts: list[Attempt]) -> np.ndarray:
        """One Observation per attempt, as the rows of an (attempts x numbers) float64 array."""
        observations = np.empty((len(attempts), OBSERVATION_LENGTH), dtype=np.float64)
        centre_columns = [_centre_column(attempt.mario) for attempt in attempts]
        observations[:, :OBSERVATION_GRID_CELLS] = self._grid_by_centre_column[centre_columns]
        for observation, attempt, centre_column in zip(observations, attempts, centre_columns):
            _mark_enemies(observation, attempt.enemies.active, centre_column - OBSERVATION_COLUMNS_BEHIND)
        np.divide([_state_quantities(attempt.mario) for attempt in attempts], self._state_divisors,
                  out=observations[:, OBSERVATION_GRID_CELLS:])
        return observations


def _state_quantities(mario: Mario) -> tuple[int, int, int, int]:
    """Mario's state in the game's integer units, each to be divided by its divisor."""
    return (mario.whole_speed_x, mario.velocity_y, mario.y + mario.height - OBSERVATION_BAND_TOP_Y,
            int(mario.is_on_ground))


def _mark_enemies(observation: np.ndarray, enemies: list[Enemy], first_column: int) -> None:
    """Each enemy marks the cell holding its hitbox centre, over whatever tile is there.
    A defeated one (a squashed Goomba) is no longer an enemy to avoid."""
    for enemy in enemies:
        if enemy.is_defeated:
            continue
        column_in_window = _centre_column(enemy) - first_column
        row_in_window = _centre_row(enemy) - OBSERVATION_TOP_ROW
        if 0 <= column_in_window < OBSERVATION_COLUMNS and 0 <= row_in_window < OBSERVATION_ROWS:
            observation[row_in_window * OBSERVATION_COLUMNS + column_in_window] = ENEMY_CELL


def _centre_column(body: TileBody) -> int:
    """The tile column holding the body's centre x; Mario's anchors the window."""
    return (body.x + body.width // 2) >> SUBPIXEL_TO_TILE_SHIFT


def _centre_row(body: TileBody) -> int:
    return (body.y + body.height // 2) >> SUBPIXEL_TO_TILE_SHIFT


def _grids_by_centre_column(level: StaticLevel) -> np.ndarray:
    """For every column Mario's centre can be in, the grid's tiles as one flat row.
    A tile shows as solid when the physics treats it so and it can be seen; columns
    outside the level do too. The hidden 1-UP block isn't solid until hit, so it
    shows empty, and so does the invisible castle stopper."""
    grids = np.empty((level.width_tiles, OBSERVATION_GRID_CELLS), dtype=np.float64)
    for centre_column in range(level.width_tiles):
        first_column = centre_column - OBSERVATION_COLUMNS_BEHIND
        cells = [SOLID_CELL if _shows_as_solid(level, column, row) else EMPTY_CELL
                 for row in range(OBSERVATION_TOP_ROW, OBSERVATION_BOTTOM_ROW + 1)
                 for column in range(first_column, first_column + OBSERVATION_COLUMNS)]
        grids[centre_column] = cells
    return grids


def _shows_as_solid(level: StaticLevel, column: int, row: int) -> bool:
    return level.is_solid(column, row) and level.tile_kind(column, row) not in INVISIBLE_SOLID_TILE_KINDS
