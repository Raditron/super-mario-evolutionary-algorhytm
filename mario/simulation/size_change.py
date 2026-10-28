"""Mario's body while he grows or shrinks (the original's PlayerChangeSize,
PlayerInjuryBlink and HandleChangeSize).

His size flips part-way into the change of his power state (PowerStateChange,
which says how long it lasts); from then on his body follows the original's
animation, a frame every 4 ticks, and once the animation is over it is his new
size until play resumes.
"""

from enum import IntEnum

from mario.constants.size_change import (
    GROW_ANIMATION_FRAMES,
    GROW_SIZE_FLIP_TICK,
    SHRINK_ANIMATION_FRAMES,
    SHRINK_SIZE_FLIP_TICK,
    SIZE_CHANGE_FRAME_TICKS,
)


class MarioBody(IntEnum):
    """The box Mario has, numbered as the animation tables number their frames."""
    SMALL = 0
    INTERMEDIATE = 1
    BIG = 2


class SizeChange:
    def __init__(self, flip_tick: int, animation_frames: tuple[int, ...],
                 body_before: MarioBody, body_after: MarioBody):
        self._flip_tick = flip_tick
        self._animation_frames = animation_frames
        self._body_before = body_before
        self._body_after = body_after
        self._ticks_elapsed = 0

    @classmethod
    def growing(cls) -> "SizeChange":
        return cls(GROW_SIZE_FLIP_TICK, GROW_ANIMATION_FRAMES, MarioBody.SMALL, MarioBody.BIG)

    @classmethod
    def shrinking(cls) -> "SizeChange":
        return cls(SHRINK_SIZE_FLIP_TICK, SHRINK_ANIMATION_FRAMES, MarioBody.BIG, MarioBody.SMALL)

    @property
    def has_flipped(self) -> bool:
        """Whether his size has flipped to the new one (the animation may still show the old)."""
        return self._ticks_elapsed >= self._flip_tick

    @property
    def shown_body(self) -> MarioBody:
        if not self.has_flipped:
            return self._body_before
        frame_index = (self._ticks_elapsed - self._flip_tick) // SIZE_CHANGE_FRAME_TICKS
        if frame_index < len(self._animation_frames):
            return MarioBody(self._animation_frames[frame_index])
        return self._body_after

    def step(self) -> None:
        self._ticks_elapsed += 1
