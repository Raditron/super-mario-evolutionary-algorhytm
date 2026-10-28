"""A body that walks along the ground, as enemies and mushrooms do (the original's
MoveNormalEnemy and EnemyToBGCollisionDet).

It walks at a steady speed, turns around at walls, and falls off ledges with
enemy gravity, still walking. It uses the same axis-separated tile collision as Mario.
"""

from mario.constants.physics import (
    BUMPED_ENEMY_LIFT_PIXELS,
    BUMPED_ENEMY_SPEED_X,
    ENEMY_GRAVITY,
    ENEMY_TERMINAL_FALL_SPEED,
    SUBPIXELS_PER_PIXEL,
)
from mario.simulation.attempt_tiles import AttemptTiles
from mario.simulation.gravity import add_gravity
from mario.simulation.tile_body import TileBody, VerticalContact


class WalkingBody(TileBody):
    def __init__(self, x: int, y: int, width: int, height: int, velocity_x: int = 0):
        super().__init__(x, y, width, height)
        self.velocity_x = velocity_x
        self.velocity_y = 0
        self.is_falling = True

    def walk(self, tiles: AttemptTiles) -> None:
        """One tick of walking: along, turning at a wall, then falling if nothing is underneath."""
        if self.move_horizontally(tiles, self._step_x()):
            self.velocity_x = -self.velocity_x
        if self.is_falling:
            self._fall(tiles)
        elif not self.is_standing_on_solid_tile(tiles):
            self.is_falling = True

    def jump_away_from(self, mario_x: int, velocity_y: int) -> None:
        """ChkToStunEnemies, SetStun, which treat every enemy object alike: lifted a
        little, it jumps at this speed and moves away from Mario."""
        self.y -= BUMPED_ENEMY_LIFT_PIXELS * SUBPIXELS_PER_PIXEL
        self.velocity_y = velocity_y
        self.velocity_x = self._speed_away_from(mario_x, BUMPED_ENEMY_SPEED_X)

    def _speed_away_from(self, mario_x: int, speed: int) -> int:
        """This speed away from Mario: rightwards if its x is at or right of his
        (PlayerEnemyDiff, EnemyFacePlayer)."""
        return speed if self.x >= mario_x else -speed

    def _step_x(self) -> int:
        """How far it moves along this tick: its walking speed."""
        return self.velocity_x

    def _fall(self, tiles: AttemptTiles) -> None:
        contact = self.move_vertically(tiles, self.velocity_y)
        self.velocity_y = add_gravity(self.velocity_y, ENEMY_GRAVITY, ENEMY_TERMINAL_FALL_SPEED)
        if contact is VerticalContact.LANDED:
            self.velocity_y = 0
            self.is_falling = False
