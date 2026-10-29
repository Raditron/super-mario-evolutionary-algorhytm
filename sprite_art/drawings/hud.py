"""The HUD's pictures: its coin icon and its font.

The coin is a round gold coin struck with a cross, as a knight's realm would mint it.
It is 7 px wide so the cross sits on its middle column; the cell's last column stays clear.

The font is one 8 x 8 glyph per character the HUD prints, of our own design: square-cornered
and blocky, every stroke 2 px wide upright and 1 px tall across, as on a stamped plate. The
letters and digits are 6 px wide (M and W, 7) and 7 px tall, from the cell's top-left corner,
all standing on the same baseline, the cell's seventh row; the cell's last row and column stay
clear so neighbouring characters stand apart. Only the curved letters' corners are cut (D, O, R),
which is also what tells the letter O from the square digit 0. The dash sits on the middle
line; the coin count's cross is as tall as the digits beside it but drawn in single-pixel
diagonals, square and lighter than any letter's stroke, so it reads as a times sign, not an X.
"""

from sprite_art.palettes.hud import HUD_PALETTE
from sprite_art.sprite_drawing import SpriteDrawing

GOLD_COIN = SpriteDrawing("coin", HUD_PALETTE, (
    "..KKK...",
    ".KLLGK..",
    "KLLdGGK.",
    "KLdddGK.",
    "KLGdGsK.",
    "KGGdGsK.",
    ".KGssK..",
    "..KKK...",
))

# --- the letters in MARIO, WORLD and TIME ---

GLYPH_A = SpriteDrawing("glyph_a", HUD_PALETTE, (
    "WWWWWW..",
    "WW..WW..",
    "WW..WW..",
    "WWWWWW..",
    "WW..WW..",
    "WW..WW..",
    "WW..WW..",
    "........",
))

GLYPH_D = SpriteDrawing("glyph_d", HUD_PALETTE, (
    "WWWWW...",
    "WW..WW..",
    "WW..WW..",
    "WW..WW..",
    "WW..WW..",
    "WW..WW..",
    "WWWWW...",
    "........",
))

GLYPH_E = SpriteDrawing("glyph_e", HUD_PALETTE, (
    "WWWWWW..",
    "WW......",
    "WW......",
    "WWWWW...",
    "WW......",
    "WW......",
    "WWWWWW..",
    "........",
))

GLYPH_I = SpriteDrawing("glyph_i", HUD_PALETTE, (
    "WWWWWW..",
    "..WW....",
    "..WW....",
    "..WW....",
    "..WW....",
    "..WW....",
    "WWWWWW..",
    "........",
))

GLYPH_L = SpriteDrawing("glyph_l", HUD_PALETTE, (
    "WW......",
    "WW......",
    "WW......",
    "WW......",
    "WW......",
    "WW......",
    "WWWWWW..",
    "........",
))

GLYPH_M = SpriteDrawing("glyph_m", HUD_PALETTE, (
    "WW...WW.",
    "WWW.WWW.",
    "WWWWWWW.",
    "WW.W.WW.",
    "WW...WW.",
    "WW...WW.",
    "WW...WW.",
    "........",
))

GLYPH_O = SpriteDrawing("glyph_o", HUD_PALETTE, (
    ".WWWW...",
    "WW..WW..",
    "WW..WW..",
    "WW..WW..",
    "WW..WW..",
    "WW..WW..",
    ".WWWW...",
    "........",
))

GLYPH_R = SpriteDrawing("glyph_r", HUD_PALETTE, (
    "WWWWW...",
    "WW..WW..",
    "WW..WW..",
    "WWWWW...",
    "WW.WW...",
    "WW..WW..",
    "WW..WW..",
    "........",
))

GLYPH_T = SpriteDrawing("glyph_t", HUD_PALETTE, (
    "WWWWWW..",
    "..WW....",
    "..WW....",
    "..WW....",
    "..WW....",
    "..WW....",
    "..WW....",
    "........",
))

GLYPH_W = SpriteDrawing("glyph_w", HUD_PALETTE, (
    "WW...WW.",
    "WW...WW.",
    "WW...WW.",
    "WW.W.WW.",
    "WWWWWWW.",
    "WWW.WWW.",
    "WW...WW.",
    "........",
))

# --- the digits ---

GLYPH_0 = SpriteDrawing("glyph_0", HUD_PALETTE, (
    "WWWWWW..",
    "WW..WW..",
    "WW..WW..",
    "WW..WW..",
    "WW..WW..",
    "WW..WW..",
    "WWWWWW..",
    "........",
))

GLYPH_1 = SpriteDrawing("glyph_1", HUD_PALETTE, (
    "..WW....",
    ".WWW....",
    "..WW....",
    "..WW....",
    "..WW....",
    "..WW....",
    "WWWWWW..",
    "........",
))

GLYPH_2 = SpriteDrawing("glyph_2", HUD_PALETTE, (
    "WWWWWW..",
    "....WW..",
    "....WW..",
    "WWWWWW..",
    "WW......",
    "WW......",
    "WWWWWW..",
    "........",
))

GLYPH_3 = SpriteDrawing("glyph_3", HUD_PALETTE, (
    "WWWWWW..",
    "....WW..",
    "....WW..",
    ".WWWWW..",
    "....WW..",
    "....WW..",
    "WWWWWW..",
    "........",
))

GLYPH_4 = SpriteDrawing("glyph_4", HUD_PALETTE, (
    "WW..WW..",
    "WW..WW..",
    "WW..WW..",
    "WWWWWW..",
    "....WW..",
    "....WW..",
    "....WW..",
    "........",
))

GLYPH_5 = SpriteDrawing("glyph_5", HUD_PALETTE, (
    "WWWWWW..",
    "WW......",
    "WW......",
    "WWWWWW..",
    "....WW..",
    "....WW..",
    "WWWWWW..",
    "........",
))

GLYPH_6 = SpriteDrawing("glyph_6", HUD_PALETTE, (
    "WWWWWW..",
    "WW......",
    "WW......",
    "WWWWWW..",
    "WW..WW..",
    "WW..WW..",
    "WWWWWW..",
    "........",
))

GLYPH_7 = SpriteDrawing("glyph_7", HUD_PALETTE, (
    "WWWWWW..",
    "....WW..",
    "....WW..",
    "...WW...",
    "..WW....",
    "..WW....",
    "..WW....",
    "........",
))

GLYPH_8 = SpriteDrawing("glyph_8", HUD_PALETTE, (
    "WWWWWW..",
    "WW..WW..",
    "WW..WW..",
    "WWWWWW..",
    "WW..WW..",
    "WW..WW..",
    "WWWWWW..",
    "........",
))

GLYPH_9 = SpriteDrawing("glyph_9", HUD_PALETTE, (
    "WWWWWW..",
    "WW..WW..",
    "WW..WW..",
    "WWWWWW..",
    "....WW..",
    "....WW..",
    "WWWWWW..",
    "........",
))

# --- the world's dash and the coin count's cross ---

GLYPH_DASH = SpriteDrawing("glyph_dash", HUD_PALETTE, (
    "........",
    "........",
    "........",
    ".WWWW...",
    "........",
    "........",
    "........",
    "........",
))

GLYPH_CROSS = SpriteDrawing("glyph_cross", HUD_PALETTE, (
    "W.....W.",
    ".W...W..",
    "..W.W...",
    "...W....",
    "..W.W...",
    ".W...W..",
    "W.....W.",
    "........",
))

HUD_GLYPH_DRAWINGS = (GLYPH_A, GLYPH_D, GLYPH_E, GLYPH_I, GLYPH_L, GLYPH_M, GLYPH_O, GLYPH_R, GLYPH_T, GLYPH_W,
                      GLYPH_0, GLYPH_1, GLYPH_2, GLYPH_3, GLYPH_4, GLYPH_5, GLYPH_6, GLYPH_7, GLYPH_8, GLYPH_9,
                      GLYPH_DASH, GLYPH_CROSS)

HUD_DRAWINGS = (GOLD_COIN,) + HUD_GLYPH_DRAWINGS
