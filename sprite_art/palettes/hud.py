"""The HUD's coin icon: its colours (RGBA), and the key each is drawn with."""

from sprite_art.palettes.shared import SHARED_KEYS

COIN_GOLD = (252, 152, 56, 255)
COIN_GOLD_LIGHT = (252, 216, 128, 255)
COIN_GOLD_SHADE = (204, 108, 32, 255)
COIN_STAMP = (148, 64, 16, 255)

HUD_PALETTE = SHARED_KEYS | {
    "G": COIN_GOLD,
    "L": COIN_GOLD_LIGHT,
    "s": COIN_GOLD_SHADE,
    "d": COIN_STAMP,
}
