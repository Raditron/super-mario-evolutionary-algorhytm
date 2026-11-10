"""The level's and the bonus room's tiles and the flag. Every tile of a kind is drawn with the same
picture, but a pipe's, upright or sideways, which is drawn by its place in its pipe."""

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

# The bonus room's exit pipe lies on its side, two tiles high: an upright pipe's
# rim and body turned so the mouth faces left, still lit from the top-left. Its
# top half's rows are the upright left half's columns, its bottom half's the right half's.
SIDE_PIPE_MOUTH_TOP = SpriteDrawing("side_pipe_mouth_top", LEVEL_PALETTE, (
    "KKKKKKKKKKKKK...",
    "KQPPPPPPPPPpK...",
    "KQQQQQQQQQQpKKKK",
    "KQQQQQQQQQQpKpPP",
    "KQQQQQQQQQQpKpQQ",
    "KQPPPPPPPPPpKpQQ",
    "KQPPPPPPPPPpKpQQ",
    "KQPPPPPPPPPpKpPP",
    "KQPPPPPPPPPpKpPP",
    "KQPPPeePPPPpKpPP",
    "KQPPPepPPPPpKpPP",
    "KQPPPPPPPPPpKpPP",
    "KQPPPPPPPPPpKpPP",
    "KQPPPPPPPPPpKpPP",
    "KQPPPPPPPPPpKpPP",
    "KQPPPPPPPPPpKpPP",
))

SIDE_PIPE_MOUTH_BOTTOM = SpriteDrawing("side_pipe_mouth_bottom", LEVEL_PALETTE, (
    "KQPPPPPPPPPpKpPP",
    "KQPPPPPPPPPpKpPP",
    "KQPPPPPPPPPpKpPP",
    "KQPPPPPPPPPpKpPP",
    "KQPPPPPPPPPpKpPP",
    "KQPPPeePPPPpKpPP",
    "KQPPPepPPPPpKpPP",
    "KQPPPPPPPPPpKpPP",
    "KQppppppppppKppp",
    "KQPPPPPPPPPpKpPP",
    "KQppppppppppKppp",
    "KQppppppppppKppp",
    "KQppppppppppKppp",
    "KQppppppppppKKKK",
    "KpppppppppppK...",
    "KKKKKKKKKKKKK...",
))

SIDE_PIPE_BODY_TOP = SpriteDrawing("side_pipe_body_top", LEVEL_PALETTE, tuple(key * 16 for key in PIPE_BODY_LEFT_ROW))

SIDE_PIPE_BODY_BOTTOM = SpriteDrawing("side_pipe_body_bottom", LEVEL_PALETTE,
                                      tuple(key * 16 for key in PIPE_BODY_RIGHT_ROW))

# Where the sideways pipe meets the upright shaft on its right: the shaft's left
# half, its outline opened to the sideways pipe, a dark seam where they join.
PIPE_JOINT_TOP = SpriteDrawing("pipe_joint_top", LEVEL_PALETTE, (
    PIPE_BODY_LEFT_ROW,
    PIPE_BODY_LEFT_ROW,
    "KKKPQQQPPPPPPPPP",
    "PPpPQQQPPPPPPPPP",
    "QQpPQQQPPPPPPPPP",
    "QQpPQQQPPPPPPPPP",
    "QQpPQQQPPPPPPPPP",
    "PPpPQQQPPPPPPPPP",
    "PPpPQQQPPPPPPPPP",
    "PPpPQQQPPPPPPPPP",
    "PPpPQQQPPPPPPPPP",
    "PPpPQQQPPPPPPPPP",
    "PPpPQQQPPPPPPPPP",
    "PPpPQQQPPPPPPPPP",
    "PPpPQQQPPPPPPPPP",
    "PPpPQQQPPPPPPPPP",
))

PIPE_JOINT_BOTTOM = SpriteDrawing("pipe_joint_bottom", LEVEL_PALETTE, (
    "PPpPQQQPPPPPPPPP",
    "PPpPQQQPPPPPPPPP",
    "PPpPQQQPPPPPPPPP",
    "PPpPQQQPPPPPPPPP",
    "PPpPQQQPPPPPPPPP",
    "PPpPQQQPPPPPPPPP",
    "PPpPQQQPPPPPPPPP",
    "PPpPQQQPPPPPPPPP",
    "pppPQQQPPPPPPPPP",
    "PPpPQQQPPPPPPPPP",
    "pppPQQQPPPPPPPPP",
    "pppPQQQPPPPPPPPP",
    "pppPQQQPPPPPPPPP",
    "KKKPQQQPPPPPPPPP",
    PIPE_BODY_LEFT_ROW,
    PIPE_BODY_LEFT_ROW,
))

# The bonus room's coins: a gold coin on its edge, as narrow as the original's
# (one 8 px column of the tile), lit on its left, a slot struck down its middle.
COIN_TILE = SpriteDrawing("coin_tile", LEVEL_PALETTE, (
    "................",
    "......KKKK......",
    ".....KZZZYK.....",
    "....KZZYYYyK....",
    "....KZYZZYyK....",
    "....KZYZYYyK....",
    "....KZYZYYyK....",
    "....KZYZYYyK....",
    "....KZYZYYyK....",
    "....KZYZYYyK....",
    "....KZYZYYyK....",
    "....KZYyyYyK....",
    "....KZYYYyyK....",
    ".....KYyyyK.....",
    "......KKKK......",
    "................",
))

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
                  PIPE_BODY_LEFT, PIPE_BODY_RIGHT, SIDE_PIPE_MOUTH_TOP, SIDE_PIPE_MOUTH_BOTTOM, SIDE_PIPE_BODY_TOP,
                  SIDE_PIPE_BODY_BOTTOM, PIPE_JOINT_TOP, PIPE_JOINT_BOTTOM, COIN_TILE, FLAGPOLE, FLAG)
