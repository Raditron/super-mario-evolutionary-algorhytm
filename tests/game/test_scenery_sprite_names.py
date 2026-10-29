"""The picture a background scenery tile is drawn with, chosen from its scenery
neighbours: a hill's slopes, peak and fill by its place in the hill, a cloud's
top and bottom rows' ends and middle by its place in the cloud, any other kind
by its own name."""

import pytest

from mario.constants.view import SPRITE_SIZES
from mario.level.background_scenery import BackgroundScenery, SceneryKind
from mario.view.scenery_sprite_names import SPRITE_NAME_RULES, SceneryNeighbourhood, scenery_sprite_name

HILL = SceneryKind.HILL
CLOUD = SceneryKind.CLOUD
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


def test_every_picture_world_1_1s_scenery_needs_is_a_sprite_the_view_knows(scenery, world_1_1):
    neighbourhoods = (SceneryNeighbourhood.around(scenery, column, row)
                      for row in range(world_1_1.height_tiles) for column in range(world_1_1.width_tiles))
    assert {scenery_sprite_name(neighbourhood) for neighbourhood in neighbourhoods
            if neighbourhood is not None} <= SPRITE_SIZES.keys()
