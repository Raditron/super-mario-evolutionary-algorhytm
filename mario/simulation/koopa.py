"""The green Koopa Troopa. It walks as a Goomba does, off ledges too (a green Koopa
doesn't turn at them).

A stomp leaves its still shell (HandleStompedShellE), which doesn't move at all,
not even to fall. Mario's touch kicks a still shell, from any side, into a moving
shell that slides away from him (HandlePECollisions), at half its speed while it
falls (MoveNormalEnemy, XSpeedAdderData), and turns at walls; a stomp stops a
moving shell again. A still shell nobody kicks wakes once its revival
timer runs out (ReviveStunned), and walks off again.

A bumped block under it doesn't defeat it but flips it into its shell (SetStun):
it hops away from Mario and, once it lands, is a still shell with its revival
timer set (ChkLandedEnemyState). While it hops, Mario's touch kicks it too.
"""

from enum import Enum, auto

from mario.constants.level import (
    KOOPA_HITBOX_HEIGHT_PIXELS,
    KOOPA_HITBOX_OFFSET_Y_PIXELS,
    KOOPA_HITBOX_WIDTH_PIXELS,
)
from mario.constants.physics import (
    AIRBORNE_SHELL_SLOWDOWN,
    BUMPED_ENEMY_SPEED_Y,
    FRAME_COUNTER_BIT_0,
    INTERVAL_TIMER_TICKS,
    KICKED_SHELL_SPEED,
    KOOPA_WALK_SPEED,
    REVIVED_KOOPA_SPEED,
    SHELL_REVIVAL_TICKS,
)
from mario.constants.scoring import KOOPA_FIREBALL_POINTS
from mario.level.static_level import EnemyKind, EnemySpawn
from mario.simulation.attempt_tiles import AttemptTiles
from mario.simulation.enemy import Enemy


class KoopaStage(Enum):
    WALKING = auto()
    BUMPED_SHELL = auto()                         # flipped by a bumped block, hopping
    STILL_SHELL = auto()
    MOVING_SHELL = auto()


class Koopa(Enemy):
    kind = EnemyKind.KOOPA
    fireball_defeat_points = KOOPA_FIREBALL_POINTS
    hitbox_offset_y_pixels = KOOPA_HITBOX_OFFSET_Y_PIXELS

    def __init__(self, spawn: EnemySpawn):
        super().__init__(spawn, KOOPA_HITBOX_WIDTH_PIXELS, KOOPA_HITBOX_HEIGHT_PIXELS, KOOPA_WALK_SPEED)
        self._stage = KoopaStage.WALKING
        self._shell_ticks_left = 0
        # The original's ShellChainCounter: the enemies it has defeated as a moving shell.
        self.shell_defeats = 0

    @property
    def is_shell(self) -> bool:
        """Once defeated, it falls out of the level flipped in its shell."""
        return self._stage is not KoopaStage.WALKING or self.is_defeated

    @property
    def is_moving_shell(self) -> bool:
        return self._stage is KoopaStage.MOVING_SHELL and not self.is_defeated

    @property
    def can_be_kicked(self) -> bool:
        return self._stage in (KoopaStage.BUMPED_SHELL, KoopaStage.STILL_SHELL) and not self.is_defeated

    @property
    def interval_ticks_left(self) -> int:
        """The original's EnemyIntervalTimer: the shell's time left before it wakes, in interval ticks."""
        return -(-self._shell_ticks_left // INTERVAL_TIMER_TICKS)

    def stomp(self) -> None:
        """A walking Koopa or a moving shell becomes a still shell, its revival timer set afresh."""
        self._stage = KoopaStage.STILL_SHELL
        self._shell_ticks_left = SHELL_REVIVAL_TICKS

    def bump_from_below(self, mario_x: int) -> None:
        """Walking or in its shell, it is flipped and hops away from Mario at once."""
        self._stage = KoopaStage.BUMPED_SHELL
        self.jump_away_from(mario_x, BUMPED_ENEMY_SPEED_Y)
        self.is_falling = True

    def kick(self, mario_x: int) -> None:
        """EnemyFacePlayer: away from Mario, rightwards if level with him."""
        self._stage = KoopaStage.MOVING_SHELL
        self.velocity_x = KICKED_SHELL_SPEED if self.x >= mario_x else -KICKED_SHELL_SPEED

    def step(self, tiles: AttemptTiles, tick: int) -> None:
        if self._stage is KoopaStage.STILL_SHELL and not self.is_defeated:
            self._count_down_to_waking(tick)
            return
        super().step(tiles, tick)
        if self._stage is KoopaStage.BUMPED_SHELL and not self.is_falling:
            self._stage = KoopaStage.STILL_SHELL
            self._shell_ticks_left = SHELL_REVIVAL_TICKS

    def _step_x(self) -> int:
        """A moving shell in the air slides slower: its speed less AIRBORNE_SHELL_SLOWDOWN."""
        if self._stage is not KoopaStage.MOVING_SHELL or not self.is_falling:
            return self.velocity_x
        slowdown = AIRBORNE_SHELL_SLOWDOWN if self.velocity_x > 0 else -AIRBORNE_SHELL_SLOWDOWN
        return self.velocity_x - slowdown

    def _count_down_to_waking(self, tick: int) -> None:
        """It wakes on the tick its timer runs out, and walks from the next."""
        self._shell_ticks_left -= 1
        if self._shell_ticks_left == 0:
            self._stage = KoopaStage.WALKING
            self.velocity_x = -REVIVED_KOOPA_SPEED if tick & FRAME_COUNTER_BIT_0 else REVIVED_KOOPA_SPEED
