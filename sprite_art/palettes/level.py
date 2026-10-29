"""The tiles' and the flag's colours (RGBA), and the key each is drawn with."""

from sprite_art.palettes.shared import SHARED_KEYS

POLE_GREY = (140, 148, 160, 255)

EARTH = (168, 104, 56, 255)
EARTH_DARK = (88, 52, 28, 255)
EARTH_LIGHT = (212, 156, 100, 255)

BRICK = (200, 72, 40, 255)
BRICK_MORTAR = (96, 28, 16, 255)
BRICK_LIGHT = (236, 128, 96, 255)

STONE = (148, 140, 156, 255)
STONE_DARK = (84, 76, 96, 255)
STONE_LIGHT = (208, 204, 216, 255)

GOLD = (248, 184, 40, 255)
GOLD_DARK = (176, 104, 16, 255)
GOLD_LIGHT = (252, 232, 140, 255)

WOOD = (136, 92, 56, 255)
WOOD_DARK = (80, 52, 32, 255)

PIPE_GREEN = (48, 168, 72, 255)
PIPE_GREEN_DARK = (16, 96, 48, 255)
PIPE_GREEN_LIGHT = (152, 228, 128, 255)

FLAG_RED = (216, 48, 40, 255)

LEVEL_PALETTE = SHARED_KEYS | {
    "e": POLE_GREY,
    "D": EARTH,
    "d": EARTH_DARK,
    "l": EARTH_LIGHT,
    "B": BRICK,
    "b": BRICK_MORTAR,
    "c": BRICK_LIGHT,
    "T": STONE,
    "t": STONE_DARK,
    "U": STONE_LIGHT,
    "Y": GOLD,
    "y": GOLD_DARK,
    "Z": GOLD_LIGHT,
    "N": WOOD,
    "n": WOOD_DARK,
    "P": PIPE_GREEN,
    "p": PIPE_GREEN_DARK,
    "Q": PIPE_GREEN_LIGHT,
    "R": FLAG_RED,
}
