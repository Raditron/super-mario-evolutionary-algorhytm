"""A hand-written test pilot: runs right and jumps at walls and pits, and at enemies if asked.

A test tool only, not an agent: it reads the Attempt directly.
"""

from mario.constants.level import TILE_SIZE_PIXELS
from mario.constants.physics import SUBPIXEL_BITS
from mario.controller.controller_state import ControllerState
from mario.simulation.attempt import Attempt

LOOK_AHEAD_PIXELS = 40

RUN_RIGHT = ControllerState.bitmask(right=True, run=True)
RUN_RIGHT_AND_JUMP = ControllerState.bitmask(right=True, run=True, jump=True)


class ScriptedPilot:
    def __init__(self, enemy_look_ahead_pixels: int | None = None):
        """enemy_look_ahead_pixels: also jump at an undefeated enemy whose left edge is at
        most this far ahead of Mario's; None ignores enemies."""
        self._enemy_look_ahead_pixels = enemy_look_ahead_pixels
        self._jump_held_last_tick = False

    def next_buttons(self, attempt: Attempt) -> int:
        mario = attempt.mario
        if mario.is_on_ground:
            wants_jump = not self._jump_held_last_tick and (
                self._wall_or_pit_ahead(attempt) or self._enemy_ahead(attempt))
        else:
            wants_jump = self._jump_held_last_tick
        self._jump_held_last_tick = wants_jump
        return RUN_RIGHT_AND_JUMP if wants_jump else RUN_RIGHT

    def _enemy_ahead(self, attempt: Attempt) -> bool:
        if self._enemy_look_ahead_pixels is None:
            return False
        return any(0 <= enemy.hitbox().x_pixels - attempt.mario.pixel_x <= self._enemy_look_ahead_pixels
                   for enemy in attempt.enemies.active if not enemy.is_defeated)

    @staticmethod
    def _wall_or_pit_ahead(attempt: Attempt) -> bool:
        mario = attempt.mario
        level = attempt.level
        right_edge_x = mario.pixel_x + (mario.width >> SUBPIXEL_BITS)
        body_rows = range(mario.pixel_y // TILE_SIZE_PIXELS,
                          (mario.pixel_y + (mario.height >> SUBPIXEL_BITS) - 1) // TILE_SIZE_PIXELS + 1)
        feet_row = (mario.pixel_y + (mario.height >> SUBPIXEL_BITS)) // TILE_SIZE_PIXELS
        for column in range(right_edge_x // TILE_SIZE_PIXELS,
                            (right_edge_x + LOOK_AHEAD_PIXELS) // TILE_SIZE_PIXELS + 1):
            if any(level.is_solid(column, row) for row in body_rows):
                return True
            if not any(level.is_solid(column, row) for row in range(feet_row, level.height_tiles)):
                return True
        return False
