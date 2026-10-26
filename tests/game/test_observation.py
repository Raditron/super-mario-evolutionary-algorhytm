"""The Observation: the 13 x 12 grid around Mario plus his four state numbers (#25, spec section 7)."""

import numpy as np
import pytest

from mario.constants.physics import SUBPIXELS_PER_PIXEL
from mario.level.static_level import StaticLevel
from mario.level.tile_kind import TileKind
from mario.simulation.attempt import Attempt
from mario.simulation.goomba import Goomba
from mario.simulation.observation_builder import ObservationBuilder
from mario.simulation.tile_body import TileBody
from tests.game.helpers import (
    HOLD_JUMP,
    HOLD_LEFT,
    HOLD_RIGHT,
    HOLD_RIGHT_RUN,
    build_level,
    goomba_spawn,
    without_enemies,
)
from tests.game.scripted_pilot import ScriptedPilot

# The layout the spec fixes: 156 grid cells, 12 rows of 13, then 4 state numbers.
GRID_ROWS, GRID_COLUMNS = 12, 13
GRID_CELLS = GRID_ROWS * GRID_COLUMNS
OBSERVATION_LENGTH = GRID_CELLS + 4
TOP_ROW = 2                                   # the grid's first row is the screen's row 2
TILE_PIXELS = 16
COLUMNS_BEHIND = 3
GROUND_ROW = 13
# World 1-1's first ? block (docs/research/world-1-1-layout.md); nothing else is above
# the ground near it.
FIRST_QUESTION_BLOCK_COLUMN, FIRST_QUESTION_BLOCK_ROW = 16, 9
TICKS_TO_REACH_THE_LEFT_EDGE = 60
TEST_LEVEL_WIDTH = 40
HIDDEN_BLOCK_COLUMN, HIDDEN_BLOCK_ROW = 5, 9  # in the window above Mario's spawn
CASTLE_STOPPER_COLUMN, CASTLE_STOPPER_ROW = 8, 12  # in the window, on the ground right of Mario's spawn
TICKS_TO_REACH_FULL_RUN_SPEED = 200
# Height runs from 0 with his feet at the band's top (row 2, y = 32) to 1 with them
# on the ground (row 13, y = 208). A standing jump with jump held rises about 66 px
# (docs/research/smb-physics-constants.md, accurate to about 1 px).
BAND_TOP_Y_PIXELS = 32
BAND_PIXELS = 208 - BAND_TOP_Y_PIXELS
HEIGHT_AT_THE_APEX = (208 - 66 - BAND_TOP_Y_PIXELS) / BAND_PIXELS
APEX_TOLERANCE = 1.5 / BAND_PIXELS
# The first tick he moves down, his speed is below one tick of the falling gravity
# (0.4375 px/f^2), as a share of the 4 px/f terminal fall.
LARGEST_SPEED_AFTER_THE_APEX = 0.4375 / 4
# The scripted pilot's attempts after these many ticks are spread over 1-1, some
# standing, some in the air, and some with a Goomba in view.
PILOT_TICKS_PER_ATTEMPT = (0, 40, 90, 130, 170, 220, 300, 420, 600)
PILOT_TICKS_WITH_GOOMBAS = 130
# The spec's divisors for the two speeds, and how far apart two ways of dividing may round.
RUN_CAP_PIXELS_PER_TICK = 2.5
TERMINAL_FALL_PIXELS_PER_TICK = 4
STATE_TOLERANCE = 1e-12


def hitbox_centre_cell(body: TileBody) -> tuple[int, int]:
    """The (column, row) of the tile holding the centre of the body's hitbox."""
    hitbox = body.hitbox()
    return ((hitbox.x_pixels + hitbox.width_pixels // 2) // TILE_PIXELS,
            (hitbox.y_pixels + hitbox.height_pixels // 2) // TILE_PIXELS)


def centre_column(attempt: Attempt) -> int:
    """The tile column holding Mario's centre x."""
    return hitbox_centre_cell(attempt.mario)[0]


def with_goomba_at(attempt: Attempt, x_pixels: int) -> Goomba:
    """Put an active Goomba at x, just spawned in row 12 above the ground, into the attempt's enemies."""
    goomba = Goomba(goomba_spawn(x_pixels))
    attempt.enemies.active.append(goomba)
    return goomba


def grid_of(observation: np.ndarray) -> np.ndarray:
    """The grid as rows (screen rows 2 to 13) of cells (3 behind Mario's column to 9 ahead)."""
    return observation[:GRID_CELLS].reshape(GRID_ROWS, GRID_COLUMNS)


def test_at_spawn_the_observation_is_160_numbers_with_the_ground_on_its_last_grid_row(world_1_1):
    observation = ObservationBuilder(world_1_1).build(Attempt(without_enemies(world_1_1)))
    assert observation.shape == (OBSERVATION_LENGTH,)
    assert observation.dtype == np.float64
    expected_grid = np.zeros((GRID_ROWS, GRID_COLUMNS))
    expected_grid[GROUND_ROW - TOP_ROW, :] = 1
    assert np.array_equal(grid_of(observation), expected_grid)


def test_cells_left_of_column_0_are_solid(world_1_1):
    attempt = Attempt(without_enemies(world_1_1))
    for _ in range(TICKS_TO_REACH_THE_LEFT_EDGE):
        attempt.step(HOLD_LEFT)
    assert centre_column(attempt) == 0
    expected_grid = np.zeros((GRID_ROWS, GRID_COLUMNS))
    expected_grid[:, :COLUMNS_BEHIND] = 1
    expected_grid[GROUND_ROW - TOP_ROW, :] = 1
    assert np.array_equal(grid_of(ObservationBuilder(world_1_1).build(attempt)), expected_grid)


@pytest.mark.parametrize("mario_centre_column", [FIRST_QUESTION_BLOCK_COLUMN - 9, FIRST_QUESTION_BLOCK_COLUMN - 4])
def test_the_first_question_block_shows_as_solid_in_its_own_cell(world_1_1, mario_centre_column):
    attempt = Attempt(without_enemies(world_1_1))
    while centre_column(attempt) < mario_centre_column:
        attempt.step(HOLD_RIGHT)
    grid = grid_of(ObservationBuilder(world_1_1).build(attempt))
    block_row = FIRST_QUESTION_BLOCK_ROW - TOP_ROW
    block_column = FIRST_QUESTION_BLOCK_COLUMN - mario_centre_column + COLUMNS_BEHIND
    assert grid[block_row, block_column] == 1
    assert grid[block_row - 1, block_column] == grid[block_row + 1, block_column] == 0
    assert grid[block_row, block_column - 1] == 0


@pytest.mark.parametrize("goomba_x, hard_blocks", [
    (112, frozenset()),                       # its hitbox fills column 7 of row 12
    (100, frozenset()),                       # it straddles columns 6 and 7; its centre is in column 6
    (112, frozenset({(7, 12)})),              # it overlaps a solid tile
])
def test_a_goomba_marks_minus_1_in_exactly_the_cell_holding_its_hitbox_centre(goomba_x, hard_blocks):
    level = build_level(hard_blocks=hard_blocks)
    attempt = Attempt(level)
    goomba = with_goomba_at(attempt, goomba_x)
    goomba_centre_column, goomba_centre_row = hitbox_centre_cell(goomba)
    grid = grid_of(ObservationBuilder(level).build(attempt))
    assert np.count_nonzero(grid == -1) == 1
    assert grid[goomba_centre_row - TOP_ROW, goomba_centre_column - centre_column(attempt) + COLUMNS_BEHIND] == -1
    assert goomba_centre_row == 12 and goomba_centre_column == goomba_x // TILE_PIXELS


def test_a_squashed_goomba_and_a_goomba_outside_the_window_are_not_shown(flat_level):
    attempt = Attempt(flat_level)
    with_goomba_at(attempt, 112).stomp()
    with_goomba_at(attempt, 13 * 16)          # Mario's centre is in column 3: the window ends at column 12
    assert not np.any(grid_of(ObservationBuilder(flat_level).build(attempt)) == -1)


def test_the_hidden_block_shows_as_empty_until_it_is_hit():
    rows = ["." * TEST_LEVEL_WIDTH] * GROUND_ROW + ["X" * TEST_LEVEL_WIDTH] * 2
    rows[HIDDEN_BLOCK_ROW] = "." * HIDDEN_BLOCK_COLUMN + "U" + "." * (TEST_LEVEL_WIDTH - HIDDEN_BLOCK_COLUMN - 1)
    level = StaticLevel(rows)
    grid = grid_of(ObservationBuilder(level).build(Attempt(level)))
    assert np.count_nonzero(grid[:GROUND_ROW - TOP_ROW]) == 0


def test_the_invisible_castle_stopper_shows_as_empty_like_the_camera_wall():
    rows = ["." * TEST_LEVEL_WIDTH] * GROUND_ROW + ["X" * TEST_LEVEL_WIDTH] * 2
    rows[CASTLE_STOPPER_ROW] = ("." * CASTLE_STOPPER_COLUMN + "W"
                                + "." * (TEST_LEVEL_WIDTH - CASTLE_STOPPER_COLUMN - 1))
    level = StaticLevel(rows)
    assert level.is_solid(CASTLE_STOPPER_COLUMN, CASTLE_STOPPER_ROW)
    grid = grid_of(ObservationBuilder(level).build(Attempt(level)))
    assert np.count_nonzero(grid[:GROUND_ROW - TOP_ROW]) == 0


def state_numbers(builder: ObservationBuilder, attempt: Attempt) -> list[float]:
    """Horizontal speed, vertical speed, height in the band and on-ground."""
    return list(builder.build(attempt)[GRID_CELLS:])


def test_standing_on_the_ground_mario_is_still_at_height_1_and_on_the_ground(flat_level):
    assert state_numbers(ObservationBuilder(flat_level), Attempt(flat_level)) == [0, 0, 1, 1]


def test_running_at_full_speed_the_horizontal_speed_is_1(flat_level):
    attempt = Attempt(flat_level)
    for _ in range(TICKS_TO_REACH_FULL_RUN_SPEED):
        attempt.step(HOLD_RIGHT_RUN)
    assert state_numbers(ObservationBuilder(flat_level), attempt) == [1, 0, 1, 1]


def test_at_the_top_of_a_standing_jump_mario_is_still_in_the_air_66_px_up(flat_level):
    builder = ObservationBuilder(flat_level)
    attempt = Attempt(flat_level)
    attempt.step(HOLD_JUMP)
    while state_numbers(builder, attempt)[1] < 0:
        attempt.step(HOLD_JUMP)
    horizontal_speed, vertical_speed, height, on_ground = state_numbers(builder, attempt)
    assert (horizontal_speed, on_ground) == (0, 0)
    assert 0 <= vertical_speed < LARGEST_SPEED_AFTER_THE_APEX
    assert height == pytest.approx(HEIGHT_AT_THE_APEX, abs=APEX_TOLERANCE)


def naive_observation(attempt: Attempt) -> np.ndarray:
    """The Observation worked out from the spec one cell at a time, apart from the builder."""
    level = attempt.level
    first_column = centre_column(attempt) - COLUMNS_BEHIND
    enemy_cells = {hitbox_centre_cell(enemy) for enemy in attempt.enemies.active if not enemy.is_defeated}
    grid = np.zeros((GRID_ROWS, GRID_COLUMNS))
    for row_in_window in range(GRID_ROWS):
        for column_in_window in range(GRID_COLUMNS):
            cell = (first_column + column_in_window, TOP_ROW + row_in_window)
            if cell in enemy_cells:
                grid[row_in_window, column_in_window] = -1
            elif level.is_solid(*cell) and level.tile_kind(*cell) is not TileKind.CASTLE_STOPPER:
                grid[row_in_window, column_in_window] = 1
    mario = attempt.mario
    feet_y_pixels = (mario.y + mario.height) / SUBPIXELS_PER_PIXEL
    state = [mario.whole_speed_x / SUBPIXELS_PER_PIXEL / RUN_CAP_PIXELS_PER_TICK,
             mario.velocity_y / SUBPIXELS_PER_PIXEL / TERMINAL_FALL_PIXELS_PER_TICK,
             (feet_y_pixels - BAND_TOP_Y_PIXELS) / BAND_PIXELS,
             1 if mario.is_on_ground else 0]
    return np.concatenate([grid.ravel(), state])


def attempts_in_different_states(world_1_1: StaticLevel) -> list[Attempt]:
    """The scripted pilot's attempts spread over 1-1, plus one walked against the left edge."""
    attempts = []
    for ticks in PILOT_TICKS_PER_ATTEMPT:
        # the pilot doesn't jump Goombas, so the longer attempts run without them
        level = world_1_1 if ticks <= PILOT_TICKS_WITH_GOOMBAS else without_enemies(world_1_1)
        attempt, pilot = Attempt(level), ScriptedPilot()
        for _ in range(ticks):
            attempt.step(pilot.next_buttons(attempt))
        attempts.append(attempt)
    at_the_left_edge = Attempt(without_enemies(world_1_1))
    for _ in range(TICKS_TO_REACH_THE_LEFT_EDGE):
        at_the_left_edge.step(HOLD_LEFT)
    attempts.append(at_the_left_edge)
    return attempts


def test_the_batched_build_matches_a_naive_cell_by_cell_observation(world_1_1):
    attempts = attempts_in_different_states(world_1_1)
    batch = ObservationBuilder(world_1_1).build_batch(attempts)
    assert batch.shape == (len(attempts), OBSERVATION_LENGTH)
    assert batch.dtype == np.float64
    for observation, attempt in zip(batch, attempts):
        expected = naive_observation(attempt)
        assert np.array_equal(observation[:GRID_CELLS], expected[:GRID_CELLS])
        assert np.allclose(observation[GRID_CELLS:], expected[GRID_CELLS:], rtol=0, atol=STATE_TOLERANCE)
    on_ground = batch[:, OBSERVATION_LENGTH - 1]
    assert np.any(batch[:, :GRID_CELLS] == -1) and np.any(on_ground == 0) and np.any(on_ground == 1)
    assert len({tuple(observation) for observation in batch}) == len(attempts)
