"""A body that walks along the ground, as enemies and mushrooms do (the original's
MoveNormalEnemy and EnemyToBGCollisionDet).

It walks at a steady speed, turns around at walls, and falls off ledges with
enemy gravity, still walking. It uses the same axis-separated tile collision as Mario.
"""

from mario.constants.physics import ENEMY_GRAVITY, ENEMY_TERMINAL_FALL_SPEED
from mario.simulation.attempt_tiles import AttemptTiles
from mario.simulation.gravity import add_gravity
from mario.simulation.tile_body import TileBody, VerticalContact


class WalkingBody(TileBody):
    def __init__(self, x: int, y: int, width: int, height: int, velocity_x: int):
        super().__init__(x, y, width, height)
        self.velocity_x = velocity_x
        self.velocity_y = 0
        self.is_falling = True

    def walk(self, tiles: AttemptTiles) -> None:
        """One tick of walking: along, turning at a wall, then falling if nothing is underneath."""
        if self.move_horizontally(tiles, self.velocity_x):
            self.velocity_x = -self.velocity_x
        if self.is_falling:
            self._fall(tiles)
        elif not self.is_standing_on_solid_tile(tiles):
            self.is_falling = True

    def _fall(self, tiles: AttemptTiles) -> None:
        contact = self.move_vertically(tiles, self.velocity_y)
        self.velocity_y = add_gravity(self.velocity_y, ENEMY_GRAVITY, ENEMY_TERMINAL_FALL_SPEED)
        if contact is VerticalContact.LANDED:
            self.velocity_y = 0
            self.is_falling = False
