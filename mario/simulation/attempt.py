"""One Attempt: one life of one Mario in a freshly loaded level.

Its only way in is step(buttons), one tick given that tick's Controller
bitmask. It uses no randomness, no floats and no wall clock, so the same
Controller log always gives the same Attempt.
"""

from mario.constants.level import PIT_DEATH_SPRITE_Y_PIXELS, SMALL_MARIO_HITBOX_OFFSET_Y_PIXELS
from mario.controller.controller_state import ControllerState
from mario.level.static_level import StaticLevel
from mario.simulation.attempt_result import AttemptResult, EndReason, GameEvent
from mario.simulation.mario import Mario
from mario.simulation.scroll import Scroll

# Points and coins arrive with the blocks, enemies and scoring slices.
NO_SCORE = 0
NO_COINS = 0


class Attempt:
    def __init__(self, level: StaticLevel):
        self.level = level
        self.mario = Mario()
        self.scroll = Scroll(self.mario.pixel_x)
        self.ticks_elapsed = 0
        self.furthest_x = self.mario.pixel_x
        self.events: list[GameEvent] = []
        self.end_reason: EndReason | None = None

    @property
    def is_over(self) -> bool:
        return self.end_reason is not None

    def step(self, buttons: int) -> None:
        if self.is_over:
            raise RuntimeError("the attempt is over")
        pixel_x_before = self.mario.pixel_x
        self.mario.step(ControllerState(buttons), self.level)
        self.scroll.follow(self.mario, self.mario.pixel_x - pixel_x_before)
        self.ticks_elapsed += 1
        self.furthest_x = max(self.furthest_x, self.mario.pixel_x)
        if self.mario.pixel_y - SMALL_MARIO_HITBOX_OFFSET_Y_PIXELS >= PIT_DEATH_SPRITE_Y_PIXELS:
            self.end_reason = EndReason.FELL_IN_PIT

    def result(self) -> AttemptResult:
        if not self.is_over:
            raise RuntimeError("the attempt is still running")
        return AttemptResult(
            end_reason=self.end_reason,
            furthest_x=self.furthest_x,
            ticks_elapsed=self.ticks_elapsed,
            final_score=NO_SCORE,
            coins_collected=NO_COINS,
            events=tuple(self.events),
        )
