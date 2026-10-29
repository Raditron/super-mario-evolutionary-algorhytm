"""The level's tiles and the flag. Every tile of a kind is drawn with the same picture, but a pipe's,
which is drawn by its place in its pipe."""

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

# A pipe is two tiles wide, drawn by place: its rim's and body's left and right
# halves. The rim is a lip the pipe's full width, banded with iron rivets, over
# the body, which is set in 2 px on each side so the lip overhangs it.
PIPE_BODY_LEFT_ROW = "..KPQQQPPPPPPPPP"
PIPE_BODY_RIGHT_ROW = "PPPPPPPPpPpppK.."

PIPE_RIM_LEFT = SpriteDrawing("pipe_rim_left", LEVEL_PALETTE, (
    "KKKKKKKKKKKKKKKK",
    "KQQQQQQQQQQQQQQQ",
    "KPQQQPPPPPPPPPPP",
    "KPQQQPPPPPPPPPPP",
    "KPQQQPPPPPPPPPPP",
    "KPQQQPPPPeePPPPP",
    "KPQQQPPPPepPPPPP",
    "KPQQQPPPPPPPPPPP",
    "KPQQQPPPPPPPPPPP",
    "KPQQQPPPPPPPPPPP",
    "KPQQQPPPPPPPPPPP",
    "Kppppppppppppppp",
    "KKKKKKKKKKKKKKKK",
    "..Kppppppppppppp",
    PIPE_BODY_LEFT_ROW,
    PIPE_BODY_LEFT_ROW,
))

PIPE_RIM_RIGHT = SpriteDrawing("pipe_rim_right", LEVEL_PALETTE, (
    "KKKKKKKKKKKKKKKK",
    "QQQQQQQQQQQQQQpK",
    "PPPPPPPPpPpppppK",
    "PPPPPPPPpPpppppK",
    "PPPPPPPPpPpppppK",
    "PPPPPeePpPpppppK",
    "PPPPPepPpPpppppK",
    "PPPPPPPPpPpppppK",
    "PPPPPPPPpPpppppK",
    "PPPPPPPPpPpppppK",
    "PPPPPPPPpPpppppK",
    "pppppppppppppppK",
    "KKKKKKKKKKKKKKKK",
    "pppppppppppppK..",
    PIPE_BODY_RIGHT_ROW,
    PIPE_BODY_RIGHT_ROW,
))

PIPE_BODY_LEFT = SpriteDrawing("pipe_body_left", LEVEL_PALETTE, (PIPE_BODY_LEFT_ROW,) * 16)

PIPE_BODY_RIGHT = SpriteDrawing("pipe_body_right", LEVEL_PALETTE, (PIPE_BODY_RIGHT_ROW,) * 16)

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

LEVEL_DRAWINGS = (GROUND, BRICK, HARD_BLOCK, QUESTION_BLOCK, USED_BLOCK, PIPE_RIM_LEFT, PIPE_RIM_RIGHT,
                  PIPE_BODY_LEFT, PIPE_BODY_RIGHT, FLAGPOLE, FLAG)
