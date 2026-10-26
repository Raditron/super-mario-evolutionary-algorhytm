"""What each tile of the level data is, and which tiles are solid."""

from enum import StrEnum


class TileKind(StrEnum):
    EMPTY = "empty"
    GROUND = "ground"
    HARD_BLOCK = "hard_block"
    BRICK = "brick"
    COIN_QUESTION_BLOCK = "coin_question_block"
    POWER_UP_QUESTION_BLOCK = "power_up_question_block"
    STARMAN_BRICK = "starman_brick"
    MULTI_COIN_BRICK = "multi_coin_brick"
    HIDDEN_ONE_UP_BLOCK = "hidden_one_up_block"
    PIPE = "pipe"
    FLAGPOLE = "flagpole"
    CASTLE_STOPPER = "castle_stopper"


# The level data's legend (mario/level/world_1_1.toml).
TILE_KIND_BY_CHARACTER = {
    ".": TileKind.EMPTY,
    "X": TileKind.GROUND,
    "#": TileKind.HARD_BLOCK,
    "B": TileKind.BRICK,
    "?": TileKind.COIN_QUESTION_BLOCK,
    "M": TileKind.POWER_UP_QUESTION_BLOCK,
    "S": TileKind.STARMAN_BRICK,
    "C": TileKind.MULTI_COIN_BRICK,
    "U": TileKind.HIDDEN_ONE_UP_BLOCK,
    "[": TileKind.PIPE,
    "]": TileKind.PIPE,
    "{": TileKind.PIPE,
    "}": TileKind.PIPE,
    "o": TileKind.FLAGPOLE,
    "|": TileKind.FLAGPOLE,
    "W": TileKind.CASTLE_STOPPER,
}

# The hidden 1-UP block becomes solid only once it is hit from below, which a
# later slice adds; the flagpole is touched, not stood on.
SOLID_TILE_KINDS = frozenset({
    TileKind.GROUND,
    TileKind.HARD_BLOCK,
    TileKind.BRICK,
    TileKind.COIN_QUESTION_BLOCK,
    TileKind.POWER_UP_QUESTION_BLOCK,
    TileKind.STARMAN_BRICK,
    TileKind.MULTI_COIN_BRICK,
    TileKind.PIPE,
    TileKind.CASTLE_STOPPER,
})

# Solid tiles nothing on screen shows: the castle stopper stands behind the castle
# art, so the Observation leaves it out, as it does the camera wall.
INVISIBLE_SOLID_TILE_KINDS = frozenset({
    TileKind.CASTLE_STOPPER,
})

# Tiles that hold something and are hit from below.
BLOCK_TILE_KINDS = frozenset({
    TileKind.BRICK,
    TileKind.COIN_QUESTION_BLOCK,
    TileKind.POWER_UP_QUESTION_BLOCK,
    TileKind.STARMAN_BRICK,
    TileKind.MULTI_COIN_BRICK,
    TileKind.HIDDEN_ONE_UP_BLOCK,
})
