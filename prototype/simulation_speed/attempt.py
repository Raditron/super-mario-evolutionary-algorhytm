"""One agent's attempt: its own Mario, its own Goombas, the shared level. PROTOTYPE.

The attempt is a pure function of the Controller buttons fed to step(): no
randomness, no wall-clock time, no floats. That is what makes replays exact.
"""

import hashlib
from collections import deque
from enum import Enum

from . import constants as c
from .goomba import Goomba
from .mario import Mario

CAMERA_FOLLOW_OFFSET = c.CAMERA_FOLLOW_OFFSET_PIXELS * c.SUBPIXELS_PER_PIXEL
ENEMY_ACTIVATION_REACH = ((c.SCREEN_WIDTH_PIXELS + c.ENEMY_ACTIVATION_DISTANCE_PIXELS)
                          * c.SUBPIXELS_PER_PIXEL)
ENEMY_DESPAWN_DISTANCE = c.ENEMY_DESPAWN_DISTANCE_PIXELS * c.SUBPIXELS_PER_PIXEL
STOMP_MAX_PENETRATION = c.STOMP_MAX_PENETRATION_PIXELS * c.SUBPIXELS_PER_PIXEL


class AttemptEnd(Enum):
    FELL_IN_PIT = "fell in pit"
    KILLED_BY_GOOMBA = "killed by Goomba"
    REACHED_FLAG = "reached flag"
    TIMER_RAN_OUT = "timer ran out"
    NO_PROGRESS = "no progress"


class Attempt:
    def __init__(self, level):
        self.level = level
        self.mario = Mario()
        self.waiting_goomba_spawns = deque(level.goomba_spawn_points_pixels())
        self.active_goombas: list[Goomba] = []
        self.camera_left = 0
        self.tick = 0
        self.best_x = self.mario.x
        self.ticks_since_progress = 0
        self.end: AttemptEnd | None = None

    @property
    def is_over(self) -> bool:
        return self.end is not None

    def step(self, buttons: int) -> None:
        level = self.level
        mario = self.mario
        mario.step(buttons, level)
        self._follow_with_camera()
        self._activate_goombas()
        for goomba in self.active_goombas:
            goomba.step(level)
        self._resolve_goomba_contacts()
        self.active_goombas = [goomba for goomba in self.active_goombas
                               if goomba.is_alive and goomba.x > self.camera_left - ENEMY_DESPAWN_DISTANCE]
        self.tick += 1
        self._check_for_end()

    def _follow_with_camera(self) -> None:
        wanted_left = self.mario.x - CAMERA_FOLLOW_OFFSET
        if wanted_left > self.camera_left:
            self.camera_left = wanted_left

    def _activate_goombas(self) -> None:
        reach = self.camera_left + ENEMY_ACTIVATION_REACH
        spawns = self.waiting_goomba_spawns
        while spawns and spawns[0][0] * c.SUBPIXELS_PER_PIXEL <= reach:
            x_pixels, y_pixels = spawns.popleft()
            self.active_goombas.append(Goomba(x_pixels, y_pixels))

    def _resolve_goomba_contacts(self) -> None:
        mario = self.mario
        for goomba in self.active_goombas:
            if not goomba.is_alive or not mario.overlaps(goomba):
                continue
            stomping = (mario.velocity_y > 0
                        and mario.y + mario.height - goomba.y <= STOMP_MAX_PENETRATION)
            if stomping:
                goomba.is_alive = False
                mario.bounce_off_stomp()
            else:
                self.end = AttemptEnd.KILLED_BY_GOOMBA
                return

    def _check_for_end(self) -> None:
        mario = self.mario
        if self.end is not None:
            return
        if mario.y >= self.level.bottom_y_subpixels:
            self.end = AttemptEnd.FELL_IN_PIT
        elif mario.x + mario.width >= self.level.flag_x_subpixels:
            self.end = AttemptEnd.REACHED_FLAG
        elif self.tick >= c.LEVEL_TIMER_TICKS:
            self.end = AttemptEnd.TIMER_RAN_OUT
        elif mario.x > self.best_x:
            self.best_x = mario.x
            self.ticks_since_progress = 0
        else:
            self.ticks_since_progress += 1
            if self.ticks_since_progress >= c.NO_PROGRESS_LIMIT_TICKS:
                self.end = AttemptEnd.NO_PROGRESS

    def state(self) -> tuple:
        """Every piece of dynamic state, as plain ints/bools/strings."""
        return (self.tick, self.end.value if self.end else None, self.camera_left, self.best_x,
                self.ticks_since_progress, self.mario.state(),
                tuple(goomba.state() for goomba in self.active_goombas),
                len(self.waiting_goomba_spawns))

    def state_digest(self) -> str:
        return hashlib.sha256(repr(self.state()).encode()).hexdigest()
