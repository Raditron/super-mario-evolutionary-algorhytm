"""The background scenery: layer 2 of the World 1-1 grid, drawing data for the
Sprite view only (docs/research/world-1-1-layout.md, spec section 4)."""

import pytest

from mario.level.background_scenery import BackgroundScenery, SceneryKind


@pytest.fixture(scope="module")
def scenery() -> BackgroundScenery:
    return BackgroundScenery.load_world_1_1()


@pytest.mark.parametrize("column, row, kind", [
    (8, 3, SceneryKind.CLOUD),
    (2, 10, SceneryKind.HILL),
    (11, 12, SceneryKind.BUSH),
    (203, 8, SceneryKind.CASTLE_BATTLEMENT),
    (203, 9, SceneryKind.CASTLE_WINDOW),
    (204, 9, SceneryKind.CASTLE_BRICK),
    (204, 11, SceneryKind.CASTLE_DOOR_ARCH),
    (204, 12, SceneryKind.CASTLE_DOOR),
])
def test_each_piece_of_scenery_is_where_the_research_grid_puts_it(scenery, column, row, kind):
    assert scenery.scenery_kind(column, row) is kind


@pytest.mark.parametrize("column, row", [(0, 0), (201, 10), (-1, 12), (224, 12), (2, 15)])
def test_open_sky_and_outside_the_grid_hold_no_scenery(scenery, column, row):
    assert scenery.scenery_kind(column, row) is None


def test_the_hills_bushes_and_clouds_repeat_every_48_columns(scenery):
    """BackSceneryData's set 2 repeats every 3 pages."""
    for column, row in [(8, 3), (2, 10), (11, 12), (19, 2)]:
        assert scenery.scenery_kind(column + 48, row) is scenery.scenery_kind(column, row)
