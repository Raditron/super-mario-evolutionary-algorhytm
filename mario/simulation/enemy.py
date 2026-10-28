"""What every walking enemy shares.

An enemy spawns at its fixed spawn position and starts walking left; it walks
as every WalkingBody does. One defeated by a bumped block or a fireball jumps up
away from Mario and falls through everything, out of the level.
"""

from abc import ABC, abstractmethod

from mario.constants.level import (
    ENEMY_FELL_OUT_SPRITE_Y_PIXELS,
    ENEMY_OFF_SCREEN_LEFT_PIXELS,
    ENEMY_OFF_SCREEN_RIGHT_X_PIXELS,
    ENEMY_SPAWN_DROP_PIXELS,
    TILE_SIZE_PIXELS,
)
from mario.constants.physics import (
    BUMP_DEFEAT_SPEED_Y,
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

    def can_be_hit_by_fireball(self, screen_left_x_pixels: int) -> bool:
        """FireballEnemyCDLoop skips a defeated enemy and one off the screen. Not
        the same as being harmful: the original's fireball also hits a Koopa's
        shell, which Mario kicks rather than gets hurt by."""
        return not self.is_defeated and not self._is_off_screen(screen_left_x_pixels)

    def _is_off_screen(self, screen_left_x_pixels: int) -> bool:
        """EnemyOffscrBitsMasked, horizontally; the enemy's x is its sprite's."""
        screen_x_pixels = self.hitbox().x_pixels - screen_left_x_pixels
        return screen_x_pixels <= -ENEMY_OFF_SCREEN_LEFT_PIXELS or screen_x_pixels >= ENEMY_OFF_SCREEN_RIGHT_X_PIXELS

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
        self.jump_away_from(mario_x, velocity_y)

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
