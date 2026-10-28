"""The flagpole: when Mario touches it, and what the touch scores.

As in the original (SideCheckLoop, HandleClimbing), he touches it with the side
probe at his sprite y + 24, on his box's left or right edge, and only where that
probe is 6 to 9 px into the pole's tile. The height of the touch (his sprite's
top) picks the points (FlagpoleYPosData), and the level timer stops there; its
units left are worth 50 points each.
"""

from dataclasses import dataclass

from mario.constants.flagpole import (
    FLAGPOLE_TOUCH_MAX_X_IN_TILE_PIXELS,
    FLAGPOLE_TOUCH_MIN_X_IN_TILE_PIXELS,
    FLAGPOLE_TOUCH_PROBE_SPRITE_Y_PIXELS,
)
from mario.constants.level import TILE_SIZE_PIXELS
from mario.constants.physics import SUBPIXEL_BITS
from mario.constants.scoring import (
    FLAGPOLE_POINTS_BY_LOWEST_SPRITE_Y_PIXELS,
    FLAGPOLE_TOP_POINTS,
    POINTS_PER_TIME_UNIT_LEFT,
)
from mario.level.tile_kind import TileKind
from mario.simulation.attempt_tiles import AttemptTiles
from mario.simulation.mario import Mario


@dataclass(frozen=True)
class FlagpoleTouch:
    """What the touch scored: the flag-height points, and the level timer's units
    left, which the remaining-time points come from."""
    flag_points: int
    time_left: int

    @property
    def time_points(self) -> int:
        return POINTS_PER_TIME_UNIT_LEFT * self.time_left

    @classmethod
    def of(cls, mario: Mario, time_left: int) -> "FlagpoleTouch":
        return cls(flag_points_for_touch_at(mario.sprite_y_pixels), time_left)


def touches_flagpole(mario: Mario, tiles: AttemptTiles) -> bool:
    probe_row = (mario.sprite_y_pixels + FLAGPOLE_TOUCH_PROBE_SPRITE_Y_PIXELS) // TILE_SIZE_PIXELS
    left_x_pixels = mario.pixel_x
    right_x_pixels = left_x_pixels + (mario.width >> SUBPIXEL_BITS) - 1
    return any(FLAGPOLE_TOUCH_MIN_X_IN_TILE_PIXELS <= probe_x_pixels % TILE_SIZE_PIXELS
               <= FLAGPOLE_TOUCH_MAX_X_IN_TILE_PIXELS
               and tiles.tile_kind(probe_x_pixels // TILE_SIZE_PIXELS, probe_row) is TileKind.FLAGPOLE
               for probe_x_pixels in (left_x_pixels, right_x_pixels))


def flag_points_for_touch_at(sprite_y_pixels: int) -> int:
    """The points for touching the pole with Mario's sprite's top at this y: the
    higher the touch, the more."""
    for lowest_sprite_y_pixels, points in FLAGPOLE_POINTS_BY_LOWEST_SPRITE_Y_PIXELS:
        if sprite_y_pixels >= lowest_sprite_y_pixels:
            return points
    return FLAGPOLE_TOP_POINTS
