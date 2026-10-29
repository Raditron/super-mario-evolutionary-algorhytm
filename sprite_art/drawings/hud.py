"""The HUD's coin icon: a round gold coin struck with a cross, as a knight's realm would mint it.
It is 7 px wide so the cross sits on its middle column; the cell's last column stays clear."""

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

HUD_DRAWINGS = (GOLD_COIN,)
