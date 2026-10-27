"""A mushroom, the Super Mushroom or the 1-UP mushroom: an item.

Once out of its block, it sets off right at 1 px/f and walks as an enemy does:
it turns at walls and falls off ledges (MoveNormalEnemy).
"""

from mario.constants.physics import (
    BUMPED_ENEMY_LIFT_PIXELS,
    BUMPED_ENEMY_SPEED_X,
    BUMPED_ENEMY_SPEED_Y,
    MUSHROOM_SPEED,
    SUBPIXELS_PER_PIXEL,
)
from mario.simulation.attempt_tiles import AttemptTiles
from mario.simulation.item import Item


class Mushroom(Item):
    def hop_away_from(self, mario_x: int) -> None:
        """ChkToStunEnemies, SetStun, which treat it as any enemy object: it is
        lifted, jumps and walks away from Mario. With nothing under it now, it
        starts to fall the tick after."""
        self.y -= BUMPED_ENEMY_LIFT_PIXELS * SUBPIXELS_PER_PIXEL
        self.velocity_y = BUMPED_ENEMY_SPEED_Y
        self.velocity_x = BUMPED_ENEMY_SPEED_X if self.x >= mario_x else -BUMPED_ENEMY_SPEED_X
        self.is_falling = False

    def _set_off(self) -> None:
        self.is_falling = False
        self.velocity_x = MUSHROOM_SPEED

    def _move(self, tiles: AttemptTiles) -> None:
        self.walk(tiles)
