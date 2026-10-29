"""The end of the level after the flagpole touch, input-free, in play and replay only.

The attempt has ended and its result is fixed; this plays out what the original
shows next, moving only the attempt's Mario and flag. The Attempt builds it at the
touch and runs it through Attempt.step_end_of_level, which also walks Mario to the
castle the way Attempt.step moves him, the screen following:

1. The flag slide (FlagpoleSlide, FlagpoleRoutine): Mario holds the pole and slides
   down until near its foot, while the flag slides down to its foot. The screen
   stays put (the touch sets ScrollLock).
2. The castle walk (PlayerEndLevel, ClimbingSub): pressing right, he hops round to
   the other side of the pole, holds on a while, lets go, and walks right until
   the castle stopper stops him at the door. The screen follows him again.
3. The timer counting down into the score (AwardGameTimerPoints): one unit a tick.

The touch already scored all its points; points_still_to_count is what the HUD
doesn't show yet: the flag-height points until the flag is down, and the
remaining-time points (POINTS_PER_TIME_UNIT_LEFT) of the time not yet counted.
Everything else (enemies, items, fireballs) stands still.
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
from mario.controller.controller_state import LEFT, RIGHT, ControllerState
from mario.simulation.attempt_tiles import AttemptTiles
from mario.simulation.flagpole import Flag, FlagpoleDescent, FlagpoleTouch, points_for_time_left
from mario.simulation.mario import Mario

# PlayerEndLevel presses right, and nothing else, until the next area.
WALK_RIGHT = ControllerState(ControllerState.bitmask(right=True))


class EndOfLevelPhase(Enum):
    TAKING_HOLD = auto()
    SLIDING = auto()
    HOPPING_ROUND_THE_POLE = auto()
    HOLDING_ON = auto()
    WALKING_TO_THE_CASTLE = auto()
    COUNTING_TIME = auto()
    OVER = auto()


class EndOfLevelSequence:
    def __init__(self, mario: Mario, tiles: AttemptTiles, flag: Flag, touch: FlagpoleTouch,
                 flagpole_column: int):
        """Built on the touch's own tick, as Mario touches the pole; nothing moves
        until the first step."""
        self._mario = mario
        self._tiles = tiles
        self._flag = flag
        self._flag_points = touch.flag_points
        self.time_left = touch.time_left
        self.phase = EndOfLevelPhase.TAKING_HOLD
        self._mario_descent = FlagpoleDescent()
        self._mario_sprite_x_pixels = flagpole_column * TILE_SIZE_PIXELS + FLAGPOLE_HOLD_SPRITE_OFFSET_X_PIXELS
        self._mario_sprite_y_pixels = mario.sprite_y_pixels
        self._hold_ticks_left = 0

    @property
    def is_over(self) -> bool:
        return self.phase is EndOfLevelPhase.OVER

    @property
    def is_walking_to_the_castle(self) -> bool:
        return self.phase is EndOfLevelPhase.WALKING_TO_THE_CASTLE

    @property
    def mario_still_moves(self) -> bool:
        """Whether Mario is still on the pole or walking to the castle: until the
        castle stopper has stopped him at the door."""
        return self.phase not in (EndOfLevelPhase.COUNTING_TIME, EndOfLevelPhase.OVER)

    @property
    def points_still_to_count(self) -> int:
        """The points of the touch the HUD's score doesn't show yet."""
        flag_is_up = self.phase in (EndOfLevelPhase.TAKING_HOLD, EndOfLevelPhase.SLIDING)
        flag_points = self._flag_points if flag_is_up else 0
        return flag_points + points_for_time_left(self.time_left)

    def step(self) -> None:
        """One tick, with no input. While walking to the castle, Mario has already
        moved this tick."""
        {
            EndOfLevelPhase.TAKING_HOLD: self._take_hold,
            EndOfLevelPhase.SLIDING: self._slide,
            EndOfLevelPhase.HOPPING_ROUND_THE_POLE: self._hop_round_the_pole,
            EndOfLevelPhase.HOLDING_ON: self._hold_on,
            EndOfLevelPhase.WALKING_TO_THE_CASTLE: self._walk_to_the_castle,
            EndOfLevelPhase.COUNTING_TIME: self._count_time,
        }[self.phase]()

    def _take_hold(self) -> None:
        """On the touch's own tick: Mario takes hold of the pole, and the flag
        already starts down (FlagpoleRoutine runs after the touch)."""
        self.phase = EndOfLevelPhase.SLIDING
        self._hold_the_pole(RIGHT)
        self._slide_the_flag()

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
        """Until the castle stopper stops him at the door."""
        if self._mario.is_flush_against_solid_tile_on_the_right(self._tiles):
            self.phase = EndOfLevelPhase.COUNTING_TIME

    def _count_time(self) -> None:
        if self.time_left == 0:
            self.phase = EndOfLevelPhase.OVER
        else:
            self.time_left = max(self.time_left - TIME_UNITS_COUNTED_PER_TICK, 0)

    def _hold_the_pole(self, facing_direction: int) -> None:
        self._mario.hold_flagpole(self._mario_sprite_x_pixels, self._mario_sprite_y_pixels, facing_direction)

