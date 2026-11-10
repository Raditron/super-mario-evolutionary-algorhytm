"""One Attempt's horizontal scroll (the original's ScrollHandler).

The screen only moves right. It starts to follow once Mario's sprite was at
least 80 px from its left edge on the previous tick, and follows at his full
speed from 112 px on. Its left edge is an invisible wall, and Mario is also kept
16 px short of its right edge.
"""

from mario.constants.level import (
    SCREEN_RIGHT_EDGE_MARGIN_PIXELS,
    SCREEN_WIDTH_PIXELS,
    SCROLL_FULL_SPEED_SCREEN_X_PIXELS,
    SCROLL_START_SCREEN_X_PIXELS,
    SCROLL_STOP_LEFT_X_PIXELS,
    SLOW_SCROLL_LAG_PIXELS,
    SLOW_SCROLL_MIN_PIXELS,
    SMALL_MARIO_HITBOX_OFFSET_X_PIXELS,
)
from mario.controller.controller_state import LEFT, RIGHT
from mario.simulation.mario import Mario

# The furthest right Mario's sprite may stand, measured from the screen's left
# edge: the original subtracts 16 px from its right edge at x + 255.
SPRITE_MAX_SCREEN_X_PIXELS = SCREEN_WIDTH_PIXELS - 1 - SCREEN_RIGHT_EDGE_MARGIN_PIXELS


class Scroll:
    def __init__(self, mario_pixel_x: int, left_x_pixels: int = 0,
                 stop_left_x_pixels: int = SCROLL_STOP_LEFT_X_PIXELS):
        """stop_left_x_pixels: the furthest right the screen's left edge goes (the
        bonus room's screen stops where it starts)."""
        self.left_x_pixels = left_x_pixels
        self._stop_left_x_pixels = stop_left_x_pixels
        self._sprite_screen_x_last_tick = mario_pixel_x - SMALL_MARIO_HITBOX_OFFSET_X_PIXELS - left_x_pixels

    def follow(self, mario: Mario, pixels_moved: int) -> None:
        """Scroll after Mario moved this tick, then keep him on screen."""
        if self._sprite_screen_x_last_tick >= SCROLL_START_SCREEN_X_PIXELS and pixels_moved > 0:
            if self._sprite_screen_x_last_tick >= SCROLL_FULL_SPEED_SCREEN_X_PIXELS:
                scroll_amount = pixels_moved
            else:
                scroll_amount = max(pixels_moved - SLOW_SCROLL_LAG_PIXELS, SLOW_SCROLL_MIN_PIXELS)
            self.left_x_pixels = min(self.left_x_pixels + scroll_amount, self._stop_left_x_pixels)
        self._keep_on_screen(mario)
        self._sprite_screen_x_last_tick = self._sprite_screen_x(mario)

    def _keep_on_screen(self, mario: Mario) -> None:
        sprite_screen_x = self._sprite_screen_x(mario)
        if sprite_screen_x <= 0:
            mario.stop_at_screen_edge(self.left_x_pixels + SMALL_MARIO_HITBOX_OFFSET_X_PIXELS,
                                      keeps_speed=mario.held_direction == RIGHT)
        elif sprite_screen_x > SPRITE_MAX_SCREEN_X_PIXELS:
            mario.stop_at_screen_edge(
                self.left_x_pixels + SPRITE_MAX_SCREEN_X_PIXELS + SMALL_MARIO_HITBOX_OFFSET_X_PIXELS,
                keeps_speed=mario.held_direction == LEFT)

    def _sprite_screen_x(self, mario: Mario) -> int:
        return mario.pixel_x - SMALL_MARIO_HITBOX_OFFSET_X_PIXELS - self.left_x_pixels
