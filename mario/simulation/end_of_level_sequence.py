"""The end of the level after the flagpole touch, input-free, in play and replay only.

The attempt has ended and its result is fixed; this plays out what the original
shows next, moving only the attempt's Mario, flag and screen:

1. The flag slide (FlagpoleSlide, FlagpoleRoutine): Mario holds the pole and slides
   down until near its foot, while the flag slides down to its foot. The screen
   stays put (the touch sets ScrollLock).
2. The castle walk (PlayerEndLevel, ClimbingSub): pressing right, he hops round to
   the other side of the pole, holds on a while, lets go, and walks right until
   the castle stopper stops him at the door. The screen follows him again.
3. The timer counting down into the score (AwardGameTimerPoints): one unit a tick.

The touch already scored all its points; points_still_to_count is what the HUD
doesn't show yet: the flag-height points until the flag is down, and 50 a unit
of time not yet counted. Everything else (enemies, items, fireballs) stands still.
"""

from enum import Enum, auto

from mario.constants.flagpole import (
    FLAG_BOTTOM_Y_PIXELS,
    FLAGPOLE_HOLD_AFTER_HOP_TICKS,
    FLAGPOLE_HOLD_SPRITE_OFFSET_X_PIXELS,
    FLAGPOLE_HOP_PIXELS,
    FLAGPOLE_LET_GO_PIXELS,
    MARIO_SLIDE_STOP_SPRITE_Y_PIXELS,
    SLIDE_END_MARIO_SPRITE_Y_PIXELS,
    TIME_UNITS_COUNTED_PER_TICK,
)
from mario.constants.level import TILE_SIZE_PIXELS
from mario.constants.scoring import POINTS_PER_TIME_UNIT_LEFT
from mario.controller.controller_state import LEFT, RIGHT, ControllerState
from mario.simulation.attempt import Attempt
from mario.simulation.flagpole import FlagpoleDescent

# PlayerEndLevel presses right, and nothing else, until the next area.
WALK_RIGHT = ControllerState(ControllerState.bitmask(right=True))


class EndOfLevelPhase(Enum):
    SLIDING = auto()
    HOPPING_ROUND_THE_POLE = auto()
    HOLDING_ON = auto()
    WALKING_TO_THE_CASTLE = auto()
    COUNTING_TIME = auto()
    OVER = auto()


class EndOfLevelSequence:
    def __init__(self, attempt: Attempt):
        """Start on the touch's own tick: Mario takes hold of the pole, and the flag
        already starts down (FlagpoleRoutine runs after the touch)."""
        if attempt.flagpole_touch is None:
            raise ValueError("the attempt did not reach the flag")
        self._mario = attempt.mario
        self._tiles = attempt.tiles
        self._scroll = attempt.scroll
        self._flag = attempt.flag
        self._flag_points = attempt.flagpole_touch.flag_points
        self.time_left = attempt.flagpole_touch.time_left
        self.phase = EndOfLevelPhase.SLIDING
        self._mario_descent = FlagpoleDescent()
        self._mario_sprite_x_pixels = (attempt.level.flagpole_column * TILE_SIZE_PIXELS
                                       + FLAGPOLE_HOLD_SPRITE_OFFSET_X_PIXELS)
        self._mario_sprite_y_pixels = self._mario.sprite_y_pixels
        self._hold_ticks_left = 0
        self._hold_the_pole(RIGHT)
        self._slide_the_flag()

    @property
    def is_over(self) -> bool:
        return self.phase is EndOfLevelPhase.OVER

    @property
    def points_still_to_count(self) -> int:
        """The points of the touch the HUD's score doesn't show yet."""
        flag_points = self._flag_points if self.phase is EndOfLevelPhase.SLIDING else 0
        return flag_points + POINTS_PER_TIME_UNIT_LEFT * self.time_left

    def step(self) -> None:
        """One tick, with no input."""
        {
            EndOfLevelPhase.SLIDING: self._slide,
            EndOfLevelPhase.HOPPING_ROUND_THE_POLE: self._hop_round_the_pole,
            EndOfLevelPhase.HOLDING_ON: self._hold_on,
            EndOfLevelPhase.WALKING_TO_THE_CASTLE: self._walk_to_the_castle,
            EndOfLevelPhase.COUNTING_TIME: self._count_time,
        }[self.phase]()

    def _slide(self) -> None:
        """FlagpoleSlide moves Mario first (pressing down until near the pole's
        foot), then FlagpoleRoutine the flag."""
        if self._mario_sprite_y_pixels < MARIO_SLIDE_STOP_SPRITE_Y_PIXELS:
            self._mario_sprite_y_pixels += self._mario_descent.next_pixels()
            self._hold_the_pole(RIGHT)
        self._slide_the_flag()

    def _slide_the_flag(self) -> None:
        """The slide ends once the flag is down, or Mario low enough."""
        if self._flag.y_pixels >= FLAG_BOTTOM_Y_PIXELS or self._mario_sprite_y_pixels >= SLIDE_END_MARIO_SPRITE_Y_PIXELS:
            self.phase = EndOfLevelPhase.HOPPING_ROUND_THE_POLE
        else:
            self._flag.slide_down()

    def _hop_round_the_pole(self) -> None:
        self._mario_sprite_x_pixels += FLAGPOLE_HOP_PIXELS
        self._hold_the_pole(LEFT)
        self._hold_ticks_left = FLAGPOLE_HOLD_AFTER_HOP_TICKS
        self.phase = EndOfLevelPhase.HOLDING_ON

    def _hold_on(self) -> None:
        """Until the climb-side timer runs out; then he moves right, off the pole,
        and lets go."""
        self._hold_ticks_left -= 1
        if self._hold_ticks_left == 0:
            self._mario_sprite_x_pixels += FLAGPOLE_LET_GO_PIXELS
            self._hold_the_pole(LEFT)
            self.phase = EndOfLevelPhase.WALKING_TO_THE_CASTLE

    def _walk_to_the_castle(self) -> None:
        pixel_x_before = self._mario.pixel_x
        self._mario.step(WALK_RIGHT, self._tiles)
        self._scroll.follow(self._mario, self._mario.pixel_x - pixel_x_before)
        if self._is_stopped_by_a_wall_on_the_right():
            self.phase = EndOfLevelPhase.COUNTING_TIME

    def _count_time(self) -> None:
        if self.time_left == 0:
            self.phase = EndOfLevelPhase.OVER
        else:
            self.time_left = max(self.time_left - TIME_UNITS_COUNTED_PER_TICK, 0)

    def _hold_the_pole(self, facing_direction: int) -> None:
        self._mario.hold_flagpole(self._mario_sprite_x_pixels, self._mario_sprite_y_pixels, facing_direction)

    def _is_stopped_by_a_wall_on_the_right(self) -> bool:
        """His box's right edge is flush against a solid tile (the castle stopper)."""
        hitbox = self._mario.hitbox()
        if hitbox.right_x_pixels % TILE_SIZE_PIXELS != 0:
            return False
        column = hitbox.right_x_pixels // TILE_SIZE_PIXELS
        rows = range(hitbox.y_pixels // TILE_SIZE_PIXELS, (hitbox.bottom_y_pixels - 1) // TILE_SIZE_PIXELS + 1)
        return any(self._tiles.is_solid(column, row) for row in rows)
