"""What every walking enemy shares (the original's MoveNormalEnemy and EnemyToBGCollisionDet).

An enemy spawns at its fixed spawn position, starts walking left, turns around
at walls, and falls off ledges with enemy gravity, still walking. It uses the
same axis-separated tile collision as Mario.
"""

from abc import ABC, abstractmethod

from mario.constants.level import ENEMY_FELL_OUT_SPRITE_Y_PIXELS, ENEMY_SPAWN_DROP_PIXELS, TILE_SIZE_PIXELS
from mario.constants.physics import ENEMY_GRAVITY, ENEMY_TERMINAL_FALL_SPEED, SUBPIXELS_PER_PIXEL
from mario.level.static_level import EnemyKind, EnemySpawn, StaticLevel
from mario.simulation.gravity import add_gravity
from mario.simulation.tile_body import TileBody, VerticalContact


class Enemy(TileBody, ABC):
    """An enemy's position is the top-left corner of its hitbox."""

    kind: EnemyKind

    def __init__(self, spawn: EnemySpawn, width_pixels: int, height_pixels: int, walk_speed: int):
        """The enemy starts at its spawn x, a little above the tile it rests on."""
        resting_top_y_pixels = spawn.resting_row * TILE_SIZE_PIXELS + TILE_SIZE_PIXELS - height_pixels
        super().__init__(spawn.x_pixels * SUBPIXELS_PER_PIXEL,
                         (resting_top_y_pixels - ENEMY_SPAWN_DROP_PIXELS) * SUBPIXELS_PER_PIXEL,
                         width_pixels * SUBPIXELS_PER_PIXEL,
                         height_pixels * SUBPIXELS_PER_PIXEL)
        self.velocity_x = -walk_speed
        self.velocity_y = 0
        self.is_falling = True

    @property
    def is_defeated(self) -> bool:
        return False

    @property
    def is_harmful(self) -> bool:
        """Whether touching it hurts Mario."""
        return not self.is_defeated

    @property
    def is_gone(self) -> bool:
        """Whether it has finished being defeated and leaves play."""
        return False

    @abstractmethod
    def stomp(self) -> None:
        """Mario landed on it."""

    @property
    def has_fallen_out(self) -> bool:
        """True once it has fallen below the screen into a pit."""
        return self.sprite_top_has_reached(ENEMY_FELL_OUT_SPRITE_Y_PIXELS)

    def step(self, level: StaticLevel) -> None:
        if self.move_horizontally(level, self.velocity_x):
            self.velocity_x = -self.velocity_x
        if self.is_falling:
            self._fall(level)
        elif not self.is_standing_on_solid_tile(level):
            self.is_falling = True

    def _fall(self, level: StaticLevel) -> None:
        contact = self.move_vertically(level, self.velocity_y)
        self.velocity_y = add_gravity(self.velocity_y, ENEMY_GRAVITY, ENEMY_TERMINAL_FALL_SPEED)
        if contact is VerticalContact.LANDED:
            self.velocity_y = 0
            self.is_falling = False
