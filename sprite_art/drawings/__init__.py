"""Every sprite drawn so far."""

from sprite_art.drawings.enemies import ENEMY_DRAWINGS
from sprite_art.drawings.fireballs import FIREBALL_DRAWINGS
from sprite_art.drawings.hud import HUD_DRAWINGS
from sprite_art.drawings.items import ITEM_DRAWINGS
from sprite_art.drawings.level import LEVEL_DRAWINGS
from sprite_art.drawings.mario import MARIO_DRAWINGS
from sprite_art.drawings.scenery import SCENERY_DRAWINGS

ALL_DRAWINGS = (LEVEL_DRAWINGS + SCENERY_DRAWINGS + MARIO_DRAWINGS + ENEMY_DRAWINGS + ITEM_DRAWINGS
                + FIREBALL_DRAWINGS + HUD_DRAWINGS)
