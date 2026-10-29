"""Which animation frame Mario shows (#57): his pose and, while he walks, which of
his three walking frames, as the original's PlayerGfxHandler picks them.

The frame is game state, so that the Sprite view keeps no clock of its own. Mario
says his pose once a tick, after everything has moved (ProcessPlayerAction); the
walk steps on through its frames, each shown for a number of ticks his speed on
the ground chose (AnimationControl, GetPlayerAnimSpeed). Every other pose sets
the walk back to its first frame. Falling off a ledge, he keeps the walking frame
he had. While his power state changes, nothing here moves.
"""

from dataclasses import dataclass, field
from enum import StrEnum

from mario.constants.animation import (
    FIRST_WALK_FRAME,
    RUN_ANIMATION_SPEED,
    RUN_TICKS_PER_WALK_FRAME,
    SLOW_TICKS_PER_WALK_FRAME,
    WALK_ANIMATION_SPEED,
    WALK_FRAME_COUNT,
    WALK_TICKS_PER_WALK_FRAME,
)


class MarioPose(StrEnum):
    """What Mario's frame shows him doing (ProcessPlayerAction's graphics table rows)."""
    STANDING = "standing"
    WALKING = "walking"
    SKIDDING = "skidding"
    JUMPING = "jumping"
    CROUCHING = "crouching"


def ticks_per_walk_frame(x_speed_absolute: int) -> int:
    """How long each walking frame shows at this speed (PlayerAnimTmrData)."""
    if x_speed_absolute >= RUN_ANIMATION_SPEED:
        return RUN_TICKS_PER_WALK_FRAME
    if x_speed_absolute >= WALK_ANIMATION_SPEED:
        return WALK_TICKS_PER_WALK_FRAME
    return SLOW_TICKS_PER_WALK_FRAME


@dataclass
class MarioAnimation:
    pose: MarioPose = MarioPose.STANDING
    walk_frame: int = FIRST_WALK_FRAME                # the walking frame shown, 1 to 3
    # PlayerAnimCtrl, counted from 1: the walking frame the walk is on
    _walk_position: int = field(default=FIRST_WALK_FRAME, init=False)
    _ticks_per_walk_frame: int = field(default=SLOW_TICKS_PER_WALK_FRAME, init=False)   # PlayerAnimTimerSet
    _walk_frame_ticks_left: int = field(default=0, init=False)                          # PlayerAnimTimer

    def choose_walk_speed(self, x_speed_absolute: int) -> None:
        """GetPlayerAnimSpeed, at the start of his tick on the ground, from his speed
        as the last tick left it. In the air the choice is kept."""
        self._ticks_per_walk_frame = ticks_per_walk_frame(x_speed_absolute)

    def show(self, pose: MarioPose) -> None:
        """Once a tick: the pose he shows. Walking, the walk shows its frame and
        steps on once that frame's time is up (AnimationControl); any other pose
        sets the walk back to its first frame (NonAnimatedActs)."""
        self._count_down()
        self.pose = pose
        if pose is not MarioPose.WALKING:
            self._walk_position = FIRST_WALK_FRAME
            self.walk_frame = FIRST_WALK_FRAME
            return
        self.walk_frame = self._walk_position
        if self._walk_frame_ticks_left == 0:
            self._walk_frame_ticks_left = self._ticks_per_walk_frame
            self._walk_position = self._walk_position % WALK_FRAME_COUNT + 1

    def keep_walk_frame(self) -> None:
        """Once a tick while he falls off a ledge (ActionFalling): the walking frame
        he had, not stepped on."""
        self._count_down()
        self.pose = MarioPose.WALKING
        self.walk_frame = self._walk_position

    def stand_through_power_state_change(self) -> None:
        """While his power state changes: standing, the walk set back to its first
        frame (InitChangeSize, for a size change; catching fire does it here too)."""
        self.pose = MarioPose.STANDING
        self._walk_position = FIRST_WALK_FRAME
        self.walk_frame = FIRST_WALK_FRAME

    def _count_down(self) -> None:
        """DecTimers, each tick the game doesn't stand still."""
        if self._walk_frame_ticks_left > 0:
            self._walk_frame_ticks_left -= 1
