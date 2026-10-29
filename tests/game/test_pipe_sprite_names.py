"""The picture a pipe tile is drawn with, chosen from its neighbouring tiles: the
rim with no pipe above it, otherwise the body; the left half with no pipe on its
left, otherwise the right half; and a tile whose left neighbour is off screen
the left half when pipe is on its right."""

import pytest

from mario.constants.view import SPRITE_SIZES
from mario.level.static_level import StaticLevel
from mario.level.tile_kind import TileKind
from mario.snapshots.world_snapshot import VISIBLE_COLUMNS, VisibleTiles
from mario.view.pipe_sprite_names import (
    PIPE_BODY_LEFT_SPRITE_NAME,
    PIPE_BODY_RIGHT_SPRITE_NAME,
    PIPE_RIM_LEFT_SPRITE_NAME,
    PIPE_RIM_RIGHT_SPRITE_NAME,
    PipeNeighbourhood,
    pipe_sprite_name,
)

PIPE, NOT_PIPE, OFF_SCREEN = True, False, None

PIPE_SPRITE_NAMES = (PIPE_RIM_LEFT_SPRITE_NAME, PIPE_RIM_RIGHT_SPRITE_NAME,
                     PIPE_BODY_LEFT_SPRITE_NAME, PIPE_BODY_RIGHT_SPRITE_NAME)

# A pipe tile's neighbours, given as (left, right, above), and the picture they pick.
PIPE_SPRITE_NAMES_BY_NEIGHBOURS = [
    pytest.param((NOT_PIPE, PIPE, NOT_PIPE), PIPE_RIM_LEFT_SPRITE_NAME, id="rim, left half"),
    pytest.param((PIPE, NOT_PIPE, NOT_PIPE), PIPE_RIM_RIGHT_SPRITE_NAME, id="rim, right half"),
    pytest.param((NOT_PIPE, PIPE, PIPE), PIPE_BODY_LEFT_SPRITE_NAME, id="body, left half"),
    pytest.param((PIPE, NOT_PIPE, PIPE), PIPE_BODY_RIGHT_SPRITE_NAME, id="body, right half"),
    pytest.param((NOT_PIPE, PIPE, OFF_SCREEN), PIPE_RIM_LEFT_SPRITE_NAME, id="nothing above the grid: rim"),
    pytest.param((OFF_SCREEN, PIPE, PIPE), PIPE_BODY_LEFT_SPRITE_NAME,
                 id="left neighbour off screen, pipe on its right: left half"),
    pytest.param((OFF_SCREEN, NOT_PIPE, PIPE), PIPE_BODY_RIGHT_SPRITE_NAME,
                 id="left neighbour off screen, no pipe on its right: right half"),
    pytest.param((NOT_PIPE, OFF_SCREEN, NOT_PIPE), PIPE_RIM_LEFT_SPRITE_NAME,
                 id="right neighbour off screen: still by its left"),
]


@pytest.mark.parametrize("neighbours, expected_sprite_name", PIPE_SPRITE_NAMES_BY_NEIGHBOURS)
def test_a_pipe_tiles_picture_is_picked_by_its_neighbouring_pipe_tiles(neighbours, expected_sprite_name):
    left, right, above = neighbours
    neighbourhood = PipeNeighbourhood(pipe_on_left=left, pipe_on_right=right, pipe_above=above)
    assert pipe_sprite_name(neighbourhood) == expected_sprite_name


def test_a_neighbour_outside_the_visible_tiles_is_none():
    """A 2 x 2 pipe filling the whole grid: its top-left tile has nothing known on its left or above it."""
    tiles = VisibleTiles(first_column=10, rows=((TileKind.PIPE, TileKind.PIPE), (TileKind.PIPE, TileKind.PIPE)))
    assert PipeNeighbourhood.around(tiles, 10, 0) == PipeNeighbourhood(
        pipe_on_left=None, pipe_on_right=True, pipe_above=None)
    assert PipeNeighbourhood.around(tiles, 11, 1) == PipeNeighbourhood(
        pipe_on_left=True, pipe_on_right=None, pipe_above=True)


def test_every_pipe_picture_is_a_sprite_the_view_knows():
    assert set(PIPE_SPRITE_NAMES) <= set(SPRITE_SIZES)
    assert "pipe" not in SPRITE_SIZES


def visible_tiles(level: StaticLevel, first_column: int, width_columns: int) -> VisibleTiles:
    return VisibleTiles(first_column, tuple(
        tuple(level.tile_kind(column, row) for column in range(first_column, first_column + width_columns))
        for row in range(level.height_tiles)))


def test_every_pipe_in_world_1_1_is_one_2_wide_pipe_with_a_rim_on_its_top_row(world_1_1):
    whole_level = visible_tiles(world_1_1, 0, world_1_1.width_tiles)
    for pipe in world_1_1.pipes:
        for row in range(pipe.top_row, pipe.top_row + pipe.height_tiles):
            left_half = pipe_sprite_name(PipeNeighbourhood.around(whole_level, pipe.left_column, row))
            right_half = pipe_sprite_name(PipeNeighbourhood.around(whole_level, pipe.left_column + 1, row))
            if row == pipe.top_row:
                assert (left_half, right_half) == (PIPE_RIM_LEFT_SPRITE_NAME, PIPE_RIM_RIGHT_SPRITE_NAME)
            else:
                assert (left_half, right_half) == (PIPE_BODY_LEFT_SPRITE_NAME, PIPE_BODY_RIGHT_SPRITE_NAME)


def test_a_pipe_tile_on_screen_picks_the_same_picture_wherever_the_screen_scrolls_to(world_1_1):
    """The snapshot holds only the columns on screen, so a pipe cut by the screen's
    left edge must still show its right half, as with the whole level in view."""
    whole_level = visible_tiles(world_1_1, 0, world_1_1.width_tiles)
    for first_column in range(world_1_1.width_tiles - VISIBLE_COLUMNS + 1):
        on_screen = visible_tiles(world_1_1, first_column, VISIBLE_COLUMNS)
        for row, kinds in enumerate(on_screen.rows):
            for column in range(first_column, first_column + VISIBLE_COLUMNS):
                if kinds[column - first_column] is TileKind.PIPE:
                    assert (pipe_sprite_name(PipeNeighbourhood.around(on_screen, column, row))
                            == pipe_sprite_name(PipeNeighbourhood.around(whole_level, column, row)))
