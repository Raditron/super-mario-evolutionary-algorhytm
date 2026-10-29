"""The picture a background scenery tile is drawn with, chosen from its scenery
neighbours: a hill's slopes, peak and fill by its place in the hill, a cloud's
top and bottom rows' ends and middle by its place in the cloud, a bush's ends
and middle by its place in the bush, the castle's edges, corner merlons and wall
top by its place in the castle, any other kind by its own name."""

import pytest

from mario.constants.view import SPRITE_SIZES
from mario.level.background_scenery import BackgroundScenery, SceneryKind
from mario.view.scenery_sprite_names import (
    CASTLE_KINDS,
    SPRITE_NAME_RULES,
    SceneryNeighbourhood,
    scenery_sprite_name,
)

HILL = SceneryKind.HILL
CLOUD = SceneryKind.CLOUD
BUSH = SceneryKind.BUSH
OPEN_SKY = None

# World 1-1's big hill (layer 2 of docs/research/world-1-1-layout.md): its peak at
# column 2 of row 10, then a row of three tiles and a row of five under it.
BIG_HILL_SPRITE_NAMES_BY_ROW = {
    10: {2: "hill_peak"},
    11: {1: "hill_left_slope", 2: "hill_fill", 3: "hill_right_slope"},
    12: {0: "hill_left_slope", 1: "hill_fill", 2: "hill_fill", 3: "hill_fill", 4: "hill_right_slope"},
}

# World 1-1's widest cloud (layer 2): columns 27-31 of rows 3 and 4.
WIDE_CLOUD_SPRITE_NAMES_BY_ROW = {
    3: {27: "cloud_top_left", 28: "cloud_top_middle", 29: "cloud_top_middle", 30: "cloud_top_middle",
        31: "cloud_top_right"},
    4: {27: "cloud_bottom_left", 28: "cloud_bottom_middle", 29: "cloud_bottom_middle", 30: "cloud_bottom_middle",
        31: "cloud_bottom_right"},
}

# World 1-1's bushes (layer 2), on row 12: the first, columns 11-15, and the one-tile
# bush against the castle at column 207, with castle wall on its left and hill on its right.
BUSH_ROW = 12
FIRST_BUSH_SPRITE_NAMES = {11: "bush_left_end", 12: "bush_middle", 13: "bush_middle", 14: "bush_middle",
                           15: "bush_right_end"}
ONE_TILE_BUSH_SPRITE_NAMES = {207: "bush_single"}
ROUNDED_ON_THE_LEFT_SPRITE_NAMES = {"bush_left_end", "bush_single"}
ROUNDED_ON_THE_RIGHT_SPRITE_NAMES = {"bush_right_end", "bush_single"}

BRICK = SceneryKind.CASTLE_BRICK
WINDOW = SceneryKind.CASTLE_WINDOW
BATTLEMENT = SceneryKind.CASTLE_BATTLEMENT

# World 1-1's castle (layer 2), columns 202-206 of rows 8-12: the tower's battlement
# and windowed wall on top of the front wall's battlement, wall, door arch and door.
CASTLE_COLUMNS = range(202, 207)
CASTLE_SPRITE_NAMES_BY_ROW = {
    8: {203: "castle_battlement_left_end", 204: "castle_battlement", 205: "castle_battlement_right_end"},
    9: {203: "castle_window_left_edge", 204: "castle_brick", 205: "castle_window_right_edge"},
    10: {202: "castle_battlement_left_end", 203: "castle_wall_top", 204: "castle_wall_top", 205: "castle_wall_top",
         206: "castle_battlement_right_end"},
    11: {202: "castle_brick_left_edge", 203: "castle_brick", 204: "castle_door_arch", 205: "castle_brick",
         206: "castle_brick_right_edge"},
    12: {202: "castle_brick_left_edge", 203: "castle_brick", 204: "castle_door", 205: "castle_brick",
         206: "castle_brick_right_edge"},
}
OUTLINED_ON_THE_LEFT_SPRITE_NAMES = {"castle_brick_left_edge", "castle_window_left_edge", "castle_battlement_left_end"}
OUTLINED_ON_THE_RIGHT_SPRITE_NAMES = {"castle_brick_right_edge", "castle_window_right_edge",
                                      "castle_battlement_right_end"}


@pytest.fixture(scope="module")
def scenery() -> BackgroundScenery:
    return BackgroundScenery.load_world_1_1()


def hill_tile(left: SceneryKind | None, right: SceneryKind | None,
              above: SceneryKind | None = OPEN_SKY) -> SceneryNeighbourhood:
    return SceneryNeighbourhood(HILL, left=left, right=right, above=above, below=OPEN_SKY)


@pytest.mark.parametrize("neighbourhood, sprite_name", [
    pytest.param(hill_tile(left=OPEN_SKY, right=OPEN_SKY), "hill_peak", id="no hill either side: peak"),
    pytest.param(hill_tile(left=OPEN_SKY, right=HILL), "hill_left_slope", id="no hill on the left: left slope"),
    pytest.param(hill_tile(left=HILL, right=OPEN_SKY), "hill_right_slope", id="no hill on the right: right slope"),
    pytest.param(hill_tile(left=HILL, right=HILL, above=HILL), "hill_fill", id="hill both sides: fill"),
    pytest.param(hill_tile(left=SceneryKind.BUSH, right=HILL), "hill_left_slope",
                 id="a bush on the left is no hill: left slope"),
])
def test_a_hill_tiles_picture_is_chosen_by_its_hill_neighbours(neighbourhood, sprite_name):
    assert scenery_sprite_name(neighbourhood) == sprite_name


def cloud_tile(left: SceneryKind | None, right: SceneryKind | None, above: SceneryKind | None) -> SceneryNeighbourhood:
    return SceneryNeighbourhood(CLOUD, left=left, right=right, above=above, below=OPEN_SKY)


@pytest.mark.parametrize("neighbourhood, sprite_name", [
    pytest.param(cloud_tile(left=OPEN_SKY, right=CLOUD, above=OPEN_SKY), "cloud_top_left",
                 id="no cloud above or on the left: top left"),
    pytest.param(cloud_tile(left=CLOUD, right=CLOUD, above=OPEN_SKY), "cloud_top_middle",
                 id="no cloud above, cloud both sides: top middle"),
    pytest.param(cloud_tile(left=CLOUD, right=OPEN_SKY, above=OPEN_SKY), "cloud_top_right",
                 id="no cloud above or on the right: top right"),
    pytest.param(cloud_tile(left=OPEN_SKY, right=CLOUD, above=CLOUD), "cloud_bottom_left",
                 id="cloud above, none on the left: bottom left"),
    pytest.param(cloud_tile(left=CLOUD, right=CLOUD, above=CLOUD), "cloud_bottom_middle",
                 id="cloud above and both sides: bottom middle"),
    pytest.param(cloud_tile(left=CLOUD, right=OPEN_SKY, above=CLOUD), "cloud_bottom_right",
                 id="cloud above, none on the right: bottom right"),
    pytest.param(cloud_tile(left=HILL, right=CLOUD, above=OPEN_SKY), "cloud_top_left",
                 id="a hill on the left is no cloud: top left"),
])
def test_a_cloud_tiles_picture_is_chosen_by_its_cloud_neighbours(neighbourhood, sprite_name):
    assert scenery_sprite_name(neighbourhood) == sprite_name


@pytest.mark.parametrize("kind", [kind for kind in SceneryKind if kind not in SPRITE_NAME_RULES])
def test_a_kind_with_no_rule_is_drawn_with_its_own_picture_wherever_it_is(kind):
    in_the_middle_of_its_kind = SceneryNeighbourhood(kind, left=kind, right=kind, above=kind, below=kind)
    assert scenery_sprite_name(in_the_middle_of_its_kind) == kind.value


def test_a_tiles_neighbourhood_is_read_from_the_scenery(scenery):
    """The big hill's left slope at (0, 12): open sky left and above, hill right, nothing under the bottom row."""
    assert SceneryNeighbourhood.around(scenery, 0, 12) == SceneryNeighbourhood(
        HILL, left=OPEN_SKY, right=HILL, above=OPEN_SKY, below=OPEN_SKY)


def test_open_sky_has_no_neighbourhood(scenery):
    assert SceneryNeighbourhood.around(scenery, 0, 0) is None


def bush_tile(left: SceneryKind | None, right: SceneryKind | None) -> SceneryNeighbourhood:
    return SceneryNeighbourhood(BUSH, left=left, right=right, above=OPEN_SKY, below=OPEN_SKY)


@pytest.mark.parametrize("neighbourhood, sprite_name", [
    pytest.param(bush_tile(left=OPEN_SKY, right=BUSH), "bush_left_end", id="no bush on the left: left end"),
    pytest.param(bush_tile(left=BUSH, right=BUSH), "bush_middle", id="bush both sides: middle"),
    pytest.param(bush_tile(left=BUSH, right=OPEN_SKY), "bush_right_end", id="no bush on the right: right end"),
    pytest.param(bush_tile(left=OPEN_SKY, right=OPEN_SKY), "bush_single", id="no bush either side: one-tile bush"),
    pytest.param(bush_tile(left=BUSH, right=HILL), "bush_right_end", id="a hill on the right is no bush: right end"),
    pytest.param(bush_tile(left=SceneryKind.CASTLE_BRICK, right=HILL), "bush_single",
                 id="castle wall and hill either side: one-tile bush"),
])
def test_a_bush_tiles_picture_is_chosen_by_its_bush_neighbours(neighbourhood, sprite_name):
    assert scenery_sprite_name(neighbourhood) == sprite_name


def castle_tile(kind: SceneryKind, left: SceneryKind | None, right: SceneryKind | None,
                above: SceneryKind | None = OPEN_SKY) -> SceneryNeighbourhood:
    return SceneryNeighbourhood(kind, left=left, right=right, above=above, below=BRICK)


@pytest.mark.parametrize("neighbourhood, sprite_name", [
    pytest.param(castle_tile(BRICK, left=OPEN_SKY, right=BRICK), "castle_brick_left_edge",
                 id="wall with no castle on the left: left edge"),
    pytest.param(castle_tile(BRICK, left=BRICK, right=SceneryKind.CASTLE_DOOR), "castle_brick",
                 id="wall with castle both sides: wall"),
    pytest.param(castle_tile(BRICK, left=BRICK, right=OPEN_SKY), "castle_brick_right_edge",
                 id="wall with no castle on the right: right edge"),
    pytest.param(castle_tile(BRICK, left=BRICK, right=BUSH), "castle_brick_right_edge",
                 id="a bush on the right is no castle: right edge"),
    pytest.param(castle_tile(WINDOW, left=OPEN_SKY, right=BRICK), "castle_window_left_edge",
                 id="window with no castle on the left: left edge"),
    pytest.param(castle_tile(WINDOW, left=BRICK, right=BRICK), "castle_window",
                 id="window with castle both sides: window"),
    pytest.param(castle_tile(WINDOW, left=BRICK, right=OPEN_SKY), "castle_window_right_edge",
                 id="window with no castle on the right: right edge"),
    pytest.param(castle_tile(BATTLEMENT, left=OPEN_SKY, right=BATTLEMENT), "castle_battlement_left_end",
                 id="battlement with no castle on the left: left corner merlon"),
    pytest.param(castle_tile(BATTLEMENT, left=BATTLEMENT, right=BATTLEMENT), "castle_battlement",
                 id="battlement with castle both sides: battlement"),
    pytest.param(castle_tile(BATTLEMENT, left=BATTLEMENT, right=OPEN_SKY), "castle_battlement_right_end",
                 id="battlement with no castle on the right: right corner merlon"),
    pytest.param(castle_tile(BATTLEMENT, left=BATTLEMENT, right=BATTLEMENT, above=WINDOW), "castle_wall_top",
                 id="battlement under the tower's window: wall top"),
    pytest.param(castle_tile(BATTLEMENT, left=OPEN_SKY, right=BATTLEMENT, above=BRICK), "castle_wall_top",
                 id="castle above outranks an edge: wall top"),
])
def test_a_castle_tiles_picture_is_chosen_by_its_place_in_the_castle(neighbourhood, sprite_name):
    assert scenery_sprite_name(neighbourhood) == sprite_name


@pytest.mark.parametrize("row", BIG_HILL_SPRITE_NAMES_BY_ROW)
def test_world_1_1s_big_hill_is_a_peak_over_slopes_and_fill(scenery, row):
    names = {column: scenery_sprite_name(SceneryNeighbourhood.around(scenery, column, row))
             for column in BIG_HILL_SPRITE_NAMES_BY_ROW[row]}
    assert names == BIG_HILL_SPRITE_NAMES_BY_ROW[row]


@pytest.mark.parametrize("row", WIDE_CLOUD_SPRITE_NAMES_BY_ROW)
def test_world_1_1s_wide_cloud_is_a_puffy_top_over_a_flat_underside(scenery, row):
    names = {column: scenery_sprite_name(SceneryNeighbourhood.around(scenery, column, row))
             for column in WIDE_CLOUD_SPRITE_NAMES_BY_ROW[row]}
    assert names == WIDE_CLOUD_SPRITE_NAMES_BY_ROW[row]


@pytest.mark.parametrize("sprite_names", [
    pytest.param(FIRST_BUSH_SPRITE_NAMES, id="the first bush: two ends and a middle"),
    pytest.param(ONE_TILE_BUSH_SPRITE_NAMES, id="the one-tile bush against the castle"),
])
def test_world_1_1s_bushes_have_rounded_ends(scenery, sprite_names):
    names = {column: scenery_sprite_name(SceneryNeighbourhood.around(scenery, column, BUSH_ROW))
             for column in sprite_names}
    assert names == sprite_names


def test_every_bush_in_world_1_1_has_rounded_ends(scenery, world_1_1):
    bush_tiles = [neighbourhood for column in range(world_1_1.width_tiles)
                  if (neighbourhood := SceneryNeighbourhood.around(scenery, column, BUSH_ROW)) is not None
                  and neighbourhood.kind is BUSH]
    assert bush_tiles
    for neighbourhood in bush_tiles:
        if neighbourhood.left is not BUSH:
            assert scenery_sprite_name(neighbourhood) in ROUNDED_ON_THE_LEFT_SPRITE_NAMES
        if neighbourhood.right is not BUSH:
            assert scenery_sprite_name(neighbourhood) in ROUNDED_ON_THE_RIGHT_SPRITE_NAMES


@pytest.mark.parametrize("row", CASTLE_SPRITE_NAMES_BY_ROW)
def test_world_1_1s_castle_has_clean_edges_and_its_tower_rises_from_a_solid_wall_top(scenery, row):
    names = {column: scenery_sprite_name(neighbourhood) for column in CASTLE_COLUMNS
             if (neighbourhood := SceneryNeighbourhood.around(scenery, column, row)) is not None}
    assert names == CASTLE_SPRITE_NAMES_BY_ROW[row]


def test_every_castle_tile_on_the_castles_edge_is_outlined_on_that_side(scenery):
    castle_tiles = [neighbourhood for row in CASTLE_SPRITE_NAMES_BY_ROW for column in CASTLE_COLUMNS
                    if (neighbourhood := SceneryNeighbourhood.around(scenery, column, row)) is not None]
    assert castle_tiles
    for neighbourhood in castle_tiles:
        if neighbourhood.left not in CASTLE_KINDS:
            assert scenery_sprite_name(neighbourhood) in OUTLINED_ON_THE_LEFT_SPRITE_NAMES
        if neighbourhood.right not in CASTLE_KINDS:
            assert scenery_sprite_name(neighbourhood) in OUTLINED_ON_THE_RIGHT_SPRITE_NAMES


def test_every_picture_world_1_1s_scenery_needs_is_a_sprite_the_view_knows(scenery, world_1_1):
    neighbourhoods = (SceneryNeighbourhood.around(scenery, column, row)
                      for row in range(world_1_1.height_tiles) for column in range(world_1_1.width_tiles))
    assert {scenery_sprite_name(neighbourhood) for neighbourhood in neighbourhoods
            if neighbourhood is not None} <= SPRITE_SIZES.keys()
