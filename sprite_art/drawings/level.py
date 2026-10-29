"""The level's tiles and the flag. Every tile of a kind is drawn with the same picture."""

from sprite_art.palettes.level import LEVEL_PALETTE
from sprite_art.sprite_drawing import SpriteDrawing

GROUND = SpriteDrawing("ground", LEVEL_PALETTE, (
    "llllllldllllllld",
    "lDDDDDDdlDDDDDDd",
    "lDDDDDDdlDDDDDDd",
    "lDDdDDDdlDDDDDDd",
    "lDDDDDDdlDDDDdDd",
    "lDDDDDDdlDDDDDDd",
    "lDDDDDDdlDDDDDDd",
    "dddddddddddddddd",
    "llllllllllllllld",
    "lDDDDDDDDDDDDDDd",
    "lDDDDDdDDDDDDDDd",
    "lDDDDDDDDDDDDDDd",
    "lDDDDDDDDDDdDDDd",
    "lDDDDDDDDDDDDDDd",
    "lDDDDDDDDDDDDDDd",
    "dddddddddddddddd",
))

BRICK = SpriteDrawing("brick", LEVEL_PALETTE, (
    "cccccccbcccccccb",
    "BBBBBBBbBBBBBBBb",
    "BBBBBBBbBBBBBBBb",
    "bbbbbbbbbbbbbbbb",
    "cccbcccccccbcccc",
    "BBBbBBBBBBBbBBBB",
    "BBBbBBBBBBBbBBBB",
    "bbbbbbbbbbbbbbbb",
    "cccccccbcccccccb",
    "BBBBBBBbBBBBBBBb",
    "BBBBBBBbBBBBBBBb",
    "bbbbbbbbbbbbbbbb",
    "cccbcccccccbcccc",
    "BBBbBBBBBBBbBBBB",
    "BBBbBBBBBBBbBBBB",
    "bbbbbbbbbbbbbbbb",
))

HARD_BLOCK = SpriteDrawing("hard_block", LEVEL_PALETTE, (
    "UUUUUUUUUUUUUUUt",
    "UUUUUUUUUUUUUUtt",
    "UUTTTTTTTTTTTTtt",
    "UUTTTTTTTTTTTTtt",
    "UUTTTTTTTTTTTTtt",
    "UUTTTtTTTTTTTTtt",
    "UUTTTTTTTTTTTTtt",
    "UUTTTTTTTTTTTTtt",
    "UUTTTTTTTTTTTTtt",
    "UUTTTTTTTTUTTTtt",
    "UUTTTTTTTTTTTTtt",
    "UUTTTTTTTTTTTTtt",
    "UUTTTTTTTTTTTTtt",
    "UUTTTTTTTTTTTTtt",
    "Uttttttttttttttt",
    "tttttttttttttttt",
))

QUESTION_BLOCK = SpriteDrawing("question_block", LEVEL_PALETTE, (
    "yyyyyyyyyyyyyyyy",
    "yZZZZZZZZZZZZZZy",
    "yZyYYYYYYYYYYyYy",
    "yZYYYYWWWWYYYYYy",
    "yZYYYWWyyWWYYYYy",
    "yZYYYWWyYWWyYYYy",
    "yZYYYYyyYWWyYYYy",
    "yZYYYYYYWWyyYYYy",
    "yZYYYYYWWyyYYYYy",
    "yZYYYYYWWyYYYYYy",
    "yZYYYYYYyyYYYYYy",
    "yZYYYYYWWYYYYYYy",
    "yZYYYYYYyyYYYYYy",
    "yZyYYYYYYYYYYyYy",
    "yZYYYYYYYYYYYYYy",
    "yyyyyyyyyyyyyyyy",
))

USED_BLOCK = SpriteDrawing("used_block", LEVEL_PALETTE, (
    "nnnnnnnnnnnnnnnn",
    "nNNNNNNNNNNNNNNn",
    "nNnNNNNNNNNNNnNn",
    "nNNNNNNNNNNNNNNn",
    "nNNNNNNNNNNNNNNn",
    "nNNNNNNNNNNNNNNn",
    "nNNNNNNNNNNNNNNn",
    "nNNNNNNNNNNNNNNn",
    "nNNNNNNNNNNNNNNn",
    "nNNNNNNNNNNNNNNn",
    "nNNNNNNNNNNNNNNn",
    "nNNNNNNNNNNNNNNn",
    "nNNNNNNNNNNNNNNn",
    "nNnNNNNNNNNNNnNn",
    "nNNNNNNNNNNNNNNn",
    "nnnnnnnnnnnnnnnn",
))

PIPE = SpriteDrawing("pipe", LEVEL_PALETTE, ("KPQQPPPPPPPPpppK",) * 16)

FLAGPOLE = SpriteDrawing("flagpole", LEVEL_PALETTE, ("......KWeK......",) * 16)

# Drawn left of the pole from its top-left corner, so it hangs from its right edge.
FLAG = SpriteDrawing("flag", LEVEL_PALETTE, (
    ".............KKK",
    "...........KRRRR",
    ".........KRRRRRR",
    ".......KRRRRRRRR",
    ".....KRRRRRRRRRR",
    "...KRRRRRWWRRRRR",
    ".KRRRRRRWWWWRRRR",
    ".KRRRRRRWWWWRRRR",
    "...KRRRRRWWRRRRR",
    ".....KRRRRRRRRRR",
    ".......KRRRRRRRR",
    ".........KRRRRRR",
    "...........KRRRR",
    ".............KKK",
    "................",
    "................",
))

LEVEL_DRAWINGS = (GROUND, BRICK, HARD_BLOCK, QUESTION_BLOCK, USED_BLOCK, PIPE, FLAGPOLE, FLAG)
