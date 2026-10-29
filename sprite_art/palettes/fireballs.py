"""Mario's fireballs: their colours (RGBA), and the key each is drawn with."""

from sprite_art.palettes.shared import SHARED_KEYS

FIRE_CORE = (255, 248, 200, 255)
FIRE_YELLOW = (252, 216, 56, 255)
FIRE_ORANGE = (240, 112, 24, 255)
FIRE_RIM = (152, 24, 16, 255)

FIREBALL_PALETTE = SHARED_KEYS | {
    "C": FIRE_CORE,
    "Y": FIRE_YELLOW,
    "O": FIRE_ORANGE,
    "r": FIRE_RIM,
}
