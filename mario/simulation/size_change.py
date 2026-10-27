"""Mario growing or shrinking (the original's PlayerChangeSize, PlayerInjuryBlink and
HandleChangeSize).

The whole game stands still while it runs. His size flips part-way in; from
then on his body follows the original's animation, a frame every 4 ticks, and
once the animation is over it is his new size until play resumes.
"""

from enum import IntEnum

from mario.constants.size_change import (
    GROW_ANIMATION_FRAMES,
    GROW_SIZE_FLIP_TICK,
    GROW_TICKS,
    SHRINK_ANIMATION_FRAMES,
    SHRINK_SIZE_FLIP_TICK,
    SHRINK_TICKS,
    SIZE_CHANGE_FRAME_TICKS,
)


class MarioBody(IntEnum):
    """The box Mario has, numbered as the animation tables number their frames."""
    SMALL = 0
    INTERMEDIATE = 1
    BIG = 2


class SizeChange:
    def __init__(self, ticks: int, flip_tick: int, animation_frames: tuple[int, ...],
                 body_before: MarioBody, body_after: MarioBody):
        self._ticks = ticks
        self._flip_tick = flip_tick
        self._animation_frames = animation_frames
        self._body_before = body_before
        self._body_after = body_after
        self._ticks_elapsed = 0

    @classmethod
    def growing(cls) -> "SizeChange":
        return cls(GROW_TICKS, GROW_SIZE_FLIP_TICK, GROW_ANIMATION_FRAMES, MarioBody.SMALL, MarioBody.BIG)

    @classmethod
    def shrinking(cls) -> "SizeChange":
        return cls(SHRINK_TICKS, SHRINK_SIZE_FLIP_TICK, SHRINK_ANIMATION_FRAMES, MarioBody.BIG, MarioBody.SMALL)

    @property
    def is_over(self) -> bool:
        return self._ticks_elapsed >= self._ticks

    @property
    def shown_body(self) -> MarioBody:
        if self._ticks_elapsed < self._flip_tick:
            return self._body_before
        frame_index = (self._ticks_elapsed - self._flip_tick) // SIZE_CHANGE_FRAME_TICKS
        if frame_index < len(self._animation_frames):
            return MarioBody(self._animation_frames[frame_index])
        return self._body_after

    def step(self) -> None:
        self._ticks_elapsed += 1
