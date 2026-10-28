"""The Goomba. A stomp squashes it: it lies flat and harmless, then disappears (ChkKillGoomba)."""

from mario.constants.level import (
    GOOMBA_HITBOX_HEIGHT_PIXELS,
    GOOMBA_HITBOX_OFFSET_Y_PIXELS,
    GOOMBA_HITBOX_WIDTH_PIXELS,
)
from mario.constants.physics import GOOMBA_WALK_SPEED, STOMPED_GOOMBA_TICKS
from mario.constants.scoring import GOOMBA_FIREBALL_POINTS
from mario.level.static_level import EnemyKind, EnemySpawn
from mario.simulation.attempt_tiles import AttemptTiles
from mario.simulation.enemy import Enemy


class Goomba(Enemy):
    kind = EnemyKind.GOOMBA
    fireball_defeat_points = GOOMBA_FIREBALL_POINTS
    hitbox_offset_y_pixels = GOOMBA_HITBOX_OFFSET_Y_PIXELS

    def __init__(self, spawn: EnemySpawn):
        super().__init__(spawn, GOOMBA_HITBOX_WIDTH_PIXELS, GOOMBA_HITBOX_HEIGHT_PIXELS, GOOMBA_WALK_SPEED)
        self._squashed_ticks_left: int | None = None

    @property
    def is_defeated(self) -> bool:
        return self._is_squashed or super().is_defeated

    @property
    def _is_squashed(self) -> bool:
        return self._squashed_ticks_left is not None

    @property
    def is_gone(self) -> bool:
        return self._squashed_ticks_left == 0

    def stomp(self) -> None:
        self._squashed_ticks_left = STOMPED_GOOMBA_TICKS

    def step(self, tiles: AttemptTiles, tick: int) -> None:
        if self._is_squashed:
            self._squashed_ticks_left -= 1
            return
        super().step(tiles, tick)
