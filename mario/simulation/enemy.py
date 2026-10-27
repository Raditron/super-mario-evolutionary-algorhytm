"""What every walking enemy shares.

An enemy spawns at its fixed spawn position and starts walking left; it walks
as every WalkingBody does. One defeated by a bumped block or a fireball jumps up
away from Mario and falls through everything, out of the level.
"""

from abc import ABC, abstractmethod

from mario.constants.level import ENEMY_FELL_OUT_SPRITE_Y_PIXELS, ENEMY_SPAWN_DROP_PIXELS, TILE_SIZE_PIXELS
from mario.constants.physics import (
    BUMP_DEFEAT_SPEED_Y,
    BUMPED_ENEMY_LIFT_PIXELS,
    BUMPED_ENEMY_SPEED_X,
    ENEMY_GRAVITY,
    ENEMY_TERMINAL_FALL_SPEED,
    FIREBALL_DEFEAT_SPEED_Y,
    SUBPIXELS_PER_PIXEL,
)
from mario.level.static_level import EnemyKind, EnemySpawn
from mario.simulation.attempt_tiles import AttemptTiles
from mario.simulation.gravity import add_gravity
from mario.simulation.walking_body import WalkingBody


class Enemy(WalkingBody, ABC):
    """An enemy's position is the top-left corner of its hitbox."""

    kind: EnemyKind
    # What defeating it with a fireball scores (ShellOrBlockDefeat).
    fireball_defeat_points: int

    def __init__(self, spawn: EnemySpawn, width_pixels: int, height_pixels: int, walk_speed: int):
        """The enemy starts at its spawn x, a little above the tile it rests on."""
        resting_top_y_pixels = spawn.resting_row * TILE_SIZE_PIXELS + TILE_SIZE_PIXELS - height_pixels
        super().__init__(spawn.x_pixels * SUBPIXELS_PER_PIXEL,
                         (resting_top_y_pixels - ENEMY_SPAWN_DROP_PIXELS) * SUBPIXELS_PER_PIXEL,
                         width_pixels * SUBPIXELS_PER_PIXEL,
                         height_pixels * SUBPIXELS_PER_PIXEL,
                         -walk_speed)
        self._is_knocked_off = False

    @property
    def is_defeated(self) -> bool:
        return self._is_knocked_off

    @property
    def is_harmful(self) -> bool:
        """Whether touching it hurts Mario."""
        return not self.is_defeated

    @property
    def can_be_hit_by_fireball(self) -> bool:
        """FireballEnemyCDLoop skips a defeated enemy."""
        return not self.is_defeated

    @property
    def is_gone(self) -> bool:
        """Whether it has finished being defeated and leaves play."""
        return False

    @abstractmethod
    def stomp(self) -> None:
        """Mario landed on it."""

    def defeat_by_bump(self, mario_x: int) -> None:
        """The block under it was bumped (KillEnemyAboveBlock, ChkToStunEnemies)."""
        self._knock_off(mario_x, BUMP_DEFEAT_SPEED_Y)

    def defeat_by_fireball(self, mario_x: int) -> None:
        """A fireball hit it (HandleEnemyFBallCol, ShellOrBlockDefeat, ChkToStunEnemies)."""
        self._knock_off(mario_x, FIREBALL_DEFEAT_SPEED_Y)

    def _knock_off(self, mario_x: int, velocity_y: int) -> None:
        """Lifted, it jumps away from Mario, and from then on falls through everything."""
        self._is_knocked_off = True
        self.y -= BUMPED_ENEMY_LIFT_PIXELS * SUBPIXELS_PER_PIXEL
        self.velocity_y = velocity_y
        self.velocity_x = BUMPED_ENEMY_SPEED_X if self.x >= mario_x else -BUMPED_ENEMY_SPEED_X

    @property
    def has_fallen_out(self) -> bool:
        """True once it has fallen below the screen into a pit."""
        return self.sprite_top_has_reached(ENEMY_FELL_OUT_SPRITE_Y_PIXELS)

    def step(self, tiles: AttemptTiles) -> None:
        if self._is_knocked_off:
            self._fall_through_everything()
            return
        self.walk(tiles)

    def _fall_through_everything(self) -> None:
        """MoveDefeatedEnemy: no tile stops it."""
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.velocity_y = add_gravity(self.velocity_y, ENEMY_GRAVITY, ENEMY_TERMINAL_FALL_SPEED)
