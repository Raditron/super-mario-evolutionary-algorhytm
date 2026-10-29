"""The picture a background scenery tile is drawn with, chosen from its scenery
neighbours, so a hill, a cloud, a bush or the castle of several tiles draws as one shape and not as
the same picture repeated.

A kind with a rule in SPRITE_NAME_RULES is drawn by place; every other kind with
the one picture its SceneryKind's value names.
"""

from collections.abc import Callable
from dataclasses import dataclass

from mario.level.background_scenery import BackgroundScenery, SceneryKind

HILL_PEAK_SPRITE_NAME = "hill_peak"
HILL_LEFT_SLOPE_SPRITE_NAME = "hill_left_slope"
HILL_RIGHT_SLOPE_SPRITE_NAME = "hill_right_slope"
HILL_FILL_SPRITE_NAME = "hill_fill"
CLOUD_TOP_LEFT_SPRITE_NAME = "cloud_top_left"
CLOUD_TOP_MIDDLE_SPRITE_NAME = "cloud_top_middle"
CLOUD_TOP_RIGHT_SPRITE_NAME = "cloud_top_right"
CLOUD_BOTTOM_LEFT_SPRITE_NAME = "cloud_bottom_left"
CLOUD_BOTTOM_MIDDLE_SPRITE_NAME = "cloud_bottom_middle"
CLOUD_BOTTOM_RIGHT_SPRITE_NAME = "cloud_bottom_right"
BUSH_LEFT_END_SPRITE_NAME = "bush_left_end"
BUSH_MIDDLE_SPRITE_NAME = "bush_middle"
BUSH_RIGHT_END_SPRITE_NAME = "bush_right_end"
BUSH_SINGLE_SPRITE_NAME = "bush_single"
CASTLE_BRICK_SPRITE_NAME = "castle_brick"
CASTLE_BRICK_LEFT_EDGE_SPRITE_NAME = "castle_brick_left_edge"
CASTLE_BRICK_RIGHT_EDGE_SPRITE_NAME = "castle_brick_right_edge"
CASTLE_WINDOW_SPRITE_NAME = "castle_window"
CASTLE_WINDOW_LEFT_EDGE_SPRITE_NAME = "castle_window_left_edge"
CASTLE_WINDOW_RIGHT_EDGE_SPRITE_NAME = "castle_window_right_edge"
CASTLE_BATTLEMENT_SPRITE_NAME = "castle_battlement"
CASTLE_BATTLEMENT_LEFT_END_SPRITE_NAME = "castle_battlement_left_end"
CASTLE_BATTLEMENT_RIGHT_END_SPRITE_NAME = "castle_battlement_right_end"
CASTLE_WALL_TOP_SPRITE_NAME = "castle_wall_top"

# Every part of the castle: a tile's side with none of these beside it is the castle's edge.
CASTLE_KINDS = frozenset({SceneryKind.CASTLE_BATTLEMENT, SceneryKind.CASTLE_WINDOW, SceneryKind.CASTLE_BRICK,
                          SceneryKind.CASTLE_DOOR_ARCH, SceneryKind.CASTLE_DOOR})


@dataclass(frozen=True)
class SceneryNeighbourhood:
    """A scenery tile's kind and its four neighbours' kinds; None is open sky or outside the grid."""

    kind: SceneryKind
    left: SceneryKind | None
    right: SceneryKind | None
    above: SceneryKind | None
    below: SceneryKind | None

    @classmethod
    def around(cls, scenery: BackgroundScenery, column: int, row: int) -> "SceneryNeighbourhood | None":
        """The tile's neighbourhood, or None for a tile of open sky."""
        kind = scenery.scenery_kind(column, row)
        if kind is None:
            return None
        return cls(kind, left=scenery.scenery_kind(column - 1, row), right=scenery.scenery_kind(column + 1, row),
                   above=scenery.scenery_kind(column, row - 1), below=scenery.scenery_kind(column, row + 1))


def scenery_sprite_name(neighbourhood: SceneryNeighbourhood) -> str:
    """The name of the sprite the tile is drawn with."""
    rule = SPRITE_NAME_RULES.get(neighbourhood.kind)
    return neighbourhood.kind.value if rule is None else rule(neighbourhood)


def _hill_sprite_name(neighbourhood: SceneryNeighbourhood) -> str:
    """A hill is a stack of rows, each one tile wider on both sides than the row
    above (layer 2 of docs/research/world-1-1-layout.md): its ends are slopes,
    a row of one tile is the peak, and the rest is fill."""
    hill_on_left = neighbourhood.left is SceneryKind.HILL
    hill_on_right = neighbourhood.right is SceneryKind.HILL
    if not hill_on_left and not hill_on_right:
        return HILL_PEAK_SPRITE_NAME
    if not hill_on_left:
        return HILL_LEFT_SLOPE_SPRITE_NAME
    if not hill_on_right:
        return HILL_RIGHT_SLOPE_SPRITE_NAME
    return HILL_FILL_SPRITE_NAME


def _cloud_sprite_name(neighbourhood: SceneryNeighbourhood) -> str:
    """A cloud is two rows of tiles, any number wide (layer 2 of
    docs/research/world-1-1-layout.md): its top row carries the puffs, its bottom
    row the flat underside, and each row's ends round off."""
    cloud_on_left = neighbourhood.left is SceneryKind.CLOUD
    cloud_on_right = neighbourhood.right is SceneryKind.CLOUD
    if neighbourhood.above is SceneryKind.CLOUD:
        if not cloud_on_left:
            return CLOUD_BOTTOM_LEFT_SPRITE_NAME
        if not cloud_on_right:
            return CLOUD_BOTTOM_RIGHT_SPRITE_NAME
        return CLOUD_BOTTOM_MIDDLE_SPRITE_NAME
    if not cloud_on_left:
        return CLOUD_TOP_LEFT_SPRITE_NAME
    if not cloud_on_right:
        return CLOUD_TOP_RIGHT_SPRITE_NAME
    return CLOUD_TOP_MIDDLE_SPRITE_NAME


def _bush_sprite_name(neighbourhood: SceneryNeighbourhood) -> str:
    """A bush is one row of tiles (layer 2 of docs/research/world-1-1-layout.md):
    its ends round off, and a bush of one tile, as World 1-1 has against the
    castle, is rounded on both sides."""
    bush_on_left = neighbourhood.left is SceneryKind.BUSH
    bush_on_right = neighbourhood.right is SceneryKind.BUSH
    if not bush_on_left and not bush_on_right:
        return BUSH_SINGLE_SPRITE_NAME
    if not bush_on_left:
        return BUSH_LEFT_END_SPRITE_NAME
    if not bush_on_right:
        return BUSH_RIGHT_END_SPRITE_NAME
    return BUSH_MIDDLE_SPRITE_NAME


def _castle_brick_sprite_name(neighbourhood: SceneryNeighbourhood) -> str:
    return _castle_wall_sprite_name(neighbourhood, CASTLE_BRICK_LEFT_EDGE_SPRITE_NAME,
                                    CASTLE_BRICK_RIGHT_EDGE_SPRITE_NAME, CASTLE_BRICK_SPRITE_NAME)


def _castle_window_sprite_name(neighbourhood: SceneryNeighbourhood) -> str:
    """World 1-1's two windows are the tower's sides (layer 2 of docs/research/world-1-1-layout.md)."""
    return _castle_wall_sprite_name(neighbourhood, CASTLE_WINDOW_LEFT_EDGE_SPRITE_NAME,
                                    CASTLE_WINDOW_RIGHT_EDGE_SPRITE_NAME, CASTLE_WINDOW_SPRITE_NAME)


def _castle_battlement_sprite_name(neighbourhood: SceneryNeighbourhood) -> str:
    """The front wall's battlement under the tower (castle above it) is the solid
    wall top the tower rises from; elsewhere a battlement's ends are corner merlons."""
    if neighbourhood.above in CASTLE_KINDS:
        return CASTLE_WALL_TOP_SPRITE_NAME
    return _castle_wall_sprite_name(neighbourhood, CASTLE_BATTLEMENT_LEFT_END_SPRITE_NAME,
                                    CASTLE_BATTLEMENT_RIGHT_END_SPRITE_NAME, CASTLE_BATTLEMENT_SPRITE_NAME)


def _castle_wall_sprite_name(neighbourhood: SceneryNeighbourhood, left_edge_sprite_name: str,
                             right_edge_sprite_name: str, inner_sprite_name: str) -> str:
    """A castle tile with no castle on its left is the castle's left edge, with
    none on its right its right edge, so the castle has a clean outline on both sides."""
    if neighbourhood.left not in CASTLE_KINDS:
        return left_edge_sprite_name
    if neighbourhood.right not in CASTLE_KINDS:
        return right_edge_sprite_name
    return inner_sprite_name


SPRITE_NAME_RULES: dict[SceneryKind, Callable[[SceneryNeighbourhood], str]] = {
    SceneryKind.HILL: _hill_sprite_name,
    SceneryKind.CLOUD: _cloud_sprite_name,
    SceneryKind.BUSH: _bush_sprite_name,
    SceneryKind.CASTLE_BRICK: _castle_brick_sprite_name,
    SceneryKind.CASTLE_WINDOW: _castle_window_sprite_name,
    SceneryKind.CASTLE_BATTLEMENT: _castle_battlement_sprite_name,
}
