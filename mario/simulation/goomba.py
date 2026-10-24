"""The Goomba. A stomp squashes it: it lies flat and harmless, then disappears (ChkKillGoomba)."""

from mario.constants.level import (
    GOOMBA_HITBOX_HEIGHT_PIXELS,
    GOOMBA_HITBOX_OFFSET_Y_PIXELS,
    GOOMBA_HITBOX_WIDTH_PIXELS,
)
from mario.constants.physics import GOOMBA_WALK_SPEED, STOMPED_GOOMBA_TICKS
from mario.level.static_level import EnemyKind, EnemySpawn, StaticLevel
from mario.simulation.enemy import Enemy


class Goomba(Enemy):
    kind = EnemyKind.GOOMBA
    hitbox_offset_y_pixels = GOOMBA_HITBOX_OFFSET_Y_PIXELS

    def __init__(self, spawn: EnemySpawn):
        super().__init__(spawn, GOOMBA_HITBOX_WIDTH_PIXELS, GOOMBA_HITBOX_HEIGHT_PIXELS, GOOMBA_WALK_SPEED)
        self._squashed_ticks_left: int | None = None

    @property
    def is_defeated(self) -> bool:
        return self._squashed_ticks_left is not None

    @property
    def is_gone(self) -> bool:
        return self._squashed_ticks_left == 0

    def stomp(self) -> None:
        self._squashed_ticks_left = STOMPED_GOOMBA_TICKS

    def step(self, level: StaticLevel) -> None:
        if self.is_defeated:
            self._squashed_ticks_left -= 1
            return
        super().step(level)
