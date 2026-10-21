"""A Goomba: walks left, turns at walls, falls into pits. PROTOTYPE."""

from . import constants as c
from .tile_body import TileBody


class Goomba(TileBody):
    __slots__ = ("is_alive",)

    def __init__(self, x_pixels: int, y_pixels: int):
        super().__init__(x_pixels, y_pixels, c.GOOMBA_SIZE_PIXELS, c.GOOMBA_SIZE_PIXELS)
        self.velocity_x = -c.GOOMBA_WALK_SPEED
        self.is_alive = True

    def step(self, level) -> None:
        self.velocity_y = min(self.velocity_y + c.ENEMY_GRAVITY, c.ENEMY_TERMINAL_FALL_SPEED)
        if self.move_horizontally(level):
            self.velocity_x = -self.velocity_x
        self.move_vertically(level)
        if self.y >= level.bottom_y_subpixels:
            self.is_alive = False

    def state(self) -> tuple:
        return (self.x, self.y, self.velocity_x, self.velocity_y, self.on_ground, self.is_alive)
