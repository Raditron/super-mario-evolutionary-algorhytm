"""The picture a background scenery tile is drawn with, chosen from its scenery
neighbours: a hill's slopes, peak and fill by its place in the hill, any other
kind by its own name."""

import pytest

from mario.constants.view import SPRITE_SIZES
from mario.level.background_scenery import BackgroundScenery, SceneryKind
from mario.view.scenery_sprite_names import SceneryNeighbourhood, scenery_sprite_name

HILL = SceneryKind.HILL
OPEN_SKY = None

# World 1-1's big hill (layer 2 of docs/research/world-1-1-layout.md): its peak at
# column 2 of row 10, then a row of three tiles and a row of five under it.
BIG_HILL_SPRITE_NAMES_BY_ROW = {
    10: {2: "hill_peak"},
    11: {1: "hill_left_slope", 2: "hill_fill", 3: "hill_right_slope"},
    12: {0: "hill_left_slope", 1: "hill_fill", 2: "hill_fill", 3: "hill_fill", 4: "hill_right_slope"},
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


def test_a_kind_with_no_rule_is_drawn_with_its_own_picture_wherever_it_is():
    cloud_in_a_cloud = SceneryNeighbourhood(SceneryKind.CLOUD, left=SceneryKind.CLOUD, right=SceneryKind.CLOUD,
                                            above=SceneryKind.CLOUD, below=OPEN_SKY)
    assert scenery_sprite_name(cloud_in_a_cloud) == "cloud"


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


def test_every_picture_world_1_1s_scenery_needs_is_a_sprite_the_view_knows(scenery, world_1_1):
    neighbourhoods = (SceneryNeighbourhood.around(scenery, column, row)
                      for row in range(world_1_1.height_tiles) for column in range(world_1_1.width_tiles))
    assert {scenery_sprite_name(neighbourhood) for neighbourhood in neighbourhoods
            if neighbourhood is not None} <= SPRITE_SIZES.keys()
