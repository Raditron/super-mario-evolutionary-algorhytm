"""The picture a background scenery tile is drawn with, chosen from its scenery
neighbours, so a hill or a cloud of several tiles draws as one shape and not as
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


SPRITE_NAME_RULES: dict[SceneryKind, Callable[[SceneryNeighbourhood], str]] = {
    SceneryKind.HILL: _hill_sprite_name,
    SceneryKind.CLOUD: _cloud_sprite_name,
}
