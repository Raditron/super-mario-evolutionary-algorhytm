"""Mario's fireballs: a flying fire bolt, and the burst it makes when it hits something."""

from sprite_art.palettes.fireballs import FIREBALL_PALETTE
from sprite_art.sprite_drawing import SpriteDrawing

FIRE_BOLT = SpriteDrawing("fireball", FIREBALL_PALETTE, (
    "..rrrr..",
    ".rOOOOr.",
    "rOYYYOOr",
    "rOYCCYOr",
    "rOYCCYOr",
    "rOOYYOOr",
    ".rOOOOr.",
    "..rrrr..",
))

FIRE_BURST = SpriteDrawing("fireball_explosion", FIREBALL_PALETTE, (
    "O......rr......O",
    ".r.....OO.....r.",
    ".......OO.......",
    "...O..rOOr..O...",
    "....rrOYYOrr....",
    "....rOYYYYOr....",
    "..rrOYYCCYYOrr..",
    ".rOOYYCCCCYYOOr.",
    ".rOOYYCCCCYYOOr.",
    "..rrOYYCCYYOrr..",
    "....rOYYYYOr....",
    "....rrOYYOrr....",
    "...O..rOOr..O...",
    ".......OO.......",
    ".r.....OO.....r.",
    "O......rr......O",
))

FIREBALL_DRAWINGS = (FIRE_BOLT, FIRE_BURST)
