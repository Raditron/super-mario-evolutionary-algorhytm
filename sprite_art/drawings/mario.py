"""Mario, drawn as a knight, by power state, facing right. One set of rows per size,
painted in each power state's palette."""

from sprite_art.palettes.mario import MARIO_FIERY_PALETTE, MARIO_INVINCIBLE_PALETTE, MARIO_PALETTE
from sprite_art.sprite_drawing import SpriteDrawing

KNIGHT_SMALL_ROWS = (
    "...KKKK.........",
    "..KPPPPK........",
    "..KPpKKKKKK.....",
    "..KpKLLLHHHK....",
    "...KLLHHHHHHK...",
    "...KLHHHHHHHK...",
    "...KHHHKKKKKK...",
    "...KHHHHHHHhK...",
    "....KhhhhhhK....",
    "..KLHKGGGGKLHK..",
    "..KLHTTTTTtHhK..",
    "..KHhTTTTttHhK..",
    "..KBBGGGGGGBBK..",
    "...KKTTTTTtKK...",
    "....KBBKKBBBK...",
    "....KKKKKKKKKK..",
)

KNIGHT_BIG_ROWS = (
    "......KKKK......",
    "....KKPPPPK.....",
    "...KPPPPPPPK....",
    "..KPPppPPpK.....",
    "..KPpKKKKKKK....",
    "..KpKKLLLHHHK...",
    "...KKLLHHHHHHK..",
    "....KLHHHHHHHK..",
    "....KLHHHHHHHK..",
    "....KHHHKKKKKK..",
    "....KHHHHHHHhK..",
    "....KHHHHHHhhK..",
    ".....KhhhhhhK...",
    "...KKKKHHHhKKK..",
    "..KLHKGGGGGKLHK.",
    "..KLHTTTTTTTHhK.",
    "..KHHTTTETTTHhK.",
    "..KHHTTEEETtHhK.",
    "..KHhTTTETTtHhK.",
    "..KHhTTTETTthhK.",
    "..KBBGGGGGGGBBK.",
    "..KBbTTTTTTtBbK.",
    "...KKTTTTTTtKK..",
    "....KTTTTTttK...",
    "....KKKKKKKKK...",
    "....KLHK.KLHK...",
    "....KHHK.KHhK...",
    "....KHhK.KHhK...",
    "....KHhK.KHhK...",
    "....KBBK.KBBK...",
    "....KBBBKKBBBbK.",
    "....KKKKKKKKKKK.",
)

MARIO_SMALL = SpriteDrawing("mario_small", MARIO_PALETTE, KNIGHT_SMALL_ROWS)
MARIO_BIG = SpriteDrawing("mario_big", MARIO_PALETTE, KNIGHT_BIG_ROWS)
MARIO_FIERY = SpriteDrawing("mario_fiery", MARIO_FIERY_PALETTE, KNIGHT_BIG_ROWS)
MARIO_SMALL_INVINCIBLE = SpriteDrawing("mario_small_invincible", MARIO_INVINCIBLE_PALETTE, KNIGHT_SMALL_ROWS)
MARIO_BIG_INVINCIBLE = SpriteDrawing("mario_big_invincible", MARIO_INVINCIBLE_PALETTE, KNIGHT_BIG_ROWS)

MARIO_DRAWINGS = (MARIO_SMALL, MARIO_BIG, MARIO_FIERY, MARIO_SMALL_INVINCIBLE, MARIO_BIG_INVINCIBLE)
