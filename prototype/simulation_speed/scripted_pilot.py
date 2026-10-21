"""A hand-written Controller policy that runs through the level. PROTOTYPE, benchmark only.

Random placeholder brains rarely get far, so their attempts are short. To time
late-generation attempts (agents crossing most of the level) the benchmark lets
this pilot press the buttons while the placeholder brain still runs every
decision tick (its output thrown away), so the per-tick cost is unchanged.
"""

from . import constants as c

SHIFT = c.SUBPIXEL_TO_TILE_SHIFT


class ScriptedPilot:
    """Hold right + run; hold jump while an obstacle, pit or Goomba is close ahead."""

    def __init__(self, level, look_ahead_tiles: int):
        self.level = level
        self.look_ahead_tiles = look_ahead_tiles

    def choose_buttons(self, attempt) -> int:
        buttons = c.BUTTON_RIGHT | c.BUTTON_RUN
        mario = attempt.mario
        if self._danger_ahead(attempt) or (not mario.on_ground and mario.velocity_y < 0):
            if mario.on_ground and mario.jump_held_last_tick:
                return buttons                         # release for one tick so the next press jumps
            buttons |= c.BUTTON_JUMP
        return buttons

    def _danger_ahead(self, attempt) -> bool:
        mario = attempt.mario
        front_column = (mario.x + mario.width) >> SHIFT
        feet_row = (mario.y + mario.height - 1) >> SHIFT
        for column in range(front_column, front_column + self.look_ahead_tiles):
            if self.level.is_solid(column, feet_row) or self.level.is_solid(column, feet_row - 1):
                return True
            if not self.level.is_solid(column, feet_row + 1):
                return True                            # pit ahead
        for goomba in attempt.active_goombas:
            distance = goomba.x - mario.x
            if 0 < distance < self.look_ahead_tiles * c.TILE_SIZE_SUBPIXELS * 2:
                return True
        return False
