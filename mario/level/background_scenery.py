"""World 1-1's background scenery: layer 2 of its grid, the clouds, hills, bushes
and castle drawn behind the tiles (docs/research/world-1-1-layout.md).

It is drawing data for the Sprite view only: never solid, and the simulation
never loads it (spec section 4).
"""

from enum import StrEnum

from mario.level.level_file import grid_layer_rows, read_level_data

LAYER_NAME = "layer_2"


class SceneryKind(StrEnum):
    # Each value is also the file name of its sprite in assets/sprites/, unless the
    # Sprite view picks the kind's picture by place (a hill's slopes, peak and fill;
    # a cloud's top and bottom rows, each with its two ends and middle).
    CLOUD = "cloud"
    HILL = "hill"
    BUSH = "bush"
    CASTLE_BATTLEMENT = "castle_battlement"
    CASTLE_WINDOW = "castle_window"
    CASTLE_BRICK = "castle_brick"
    CASTLE_DOOR_ARCH = "castle_door_arch"
    CASTLE_DOOR = "castle_door"


OPEN_SKY_CHARACTER = "."
# The level data's legend for layer 2.
SCENERY_KIND_BY_CHARACTER = {
    "c": SceneryKind.CLOUD,
    "h": SceneryKind.HILL,
    "b": SceneryKind.BUSH,
    "^": SceneryKind.CASTLE_BATTLEMENT,
    "w": SceneryKind.CASTLE_WINDOW,
    "=": SceneryKind.CASTLE_BRICK,
    "(": SceneryKind.CASTLE_DOOR_ARCH,
    "D": SceneryKind.CASTLE_DOOR,
}


class BackgroundScenery:
    def __init__(self, layer_2_rows: list[str]):
        self._kind_rows = tuple(tuple(_scenery_kind_of(character) for character in row) for row in layer_2_rows)

    @classmethod
    def load_world_1_1(cls) -> "BackgroundScenery":
        return cls(grid_layer_rows(read_level_data(), LAYER_NAME))

    def scenery_kind(self, column: int, row: int) -> SceneryKind | None:
        """What stands in the tile, or None for open sky and outside the grid."""
        if not (0 <= row < len(self._kind_rows) and 0 <= column < len(self._kind_rows[row])):
            return None
        return self._kind_rows[row][column]


def _scenery_kind_of(character: str) -> SceneryKind | None:
    return None if character == OPEN_SKY_CHARACTER else SCENERY_KIND_BY_CHARACTER[character]
