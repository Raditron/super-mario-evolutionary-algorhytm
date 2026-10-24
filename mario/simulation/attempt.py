"""One Attempt: one life of one Mario in a freshly loaded level.

Its only way in is step(buttons), one tick given that tick's Controller
bitmask. It uses no randomness, no floats and no wall clock, so the same
Controller log always gives the same Attempt.

It ends when Mario dies or the level timer runs out, and, if the mode turns
the stall rule on (training does, play doesn't), when he stalls.
"""

from mario.constants.level import (
    CHECKPOINT_LEFT_X_PIXELS,
    PIT_DEATH_SPRITE_Y_PIXELS,
    SMALL_MARIO_HITBOX_OFFSET_Y_PIXELS,
)
from mario.controller.controller_state import ControllerState
from mario.level.static_level import StaticLevel
from mario.simulation.attempt_result import AttemptResult, EndReason, GameEvent
from mario.simulation.level_timer import LevelTimer
from mario.simulation.mario import Mario
from mario.simulation.scoreboard import Scoreboard
from mario.simulation.scroll import Scroll
from mario.simulation.stall_rule import StallRule


class Attempt:
    def __init__(self, level: StaticLevel, *, ends_on_stall: bool = False, from_checkpoint: bool = False):
        """ends_on_stall turns the stall rule on. from_checkpoint starts Mario
        with the screen's left edge at the checkpoint (play mode only)."""
        screen_left_x_pixels = CHECKPOINT_LEFT_X_PIXELS if from_checkpoint else 0
        self.level = level
        self.mario = Mario(screen_left_x_pixels)
        self.scroll = Scroll(self.mario.pixel_x, screen_left_x_pixels)
        self.level_timer = LevelTimer()
        self.ticks_elapsed = 0
        self.furthest_x = self.mario.pixel_x
        self.events: list[GameEvent] = []
        self.scoreboard = Scoreboard(self.events)
        self._stall_rule = StallRule(self.mario.pixel_x) if ends_on_stall else None
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
        self.level_timer.count_down()
        if self._stall_rule is not None:
            self._stall_rule.observe(self.mario.pixel_x)
        self.end_reason = self._reason_to_end()

    def result(self) -> AttemptResult:
        if not self.is_over:
            raise RuntimeError("the attempt is still running")
        return AttemptResult(
            end_reason=self.end_reason,
            furthest_x=self.furthest_x,
            ticks_elapsed=self.ticks_elapsed,
            final_score=self.scoreboard.score,
            coins_collected=self.scoreboard.coins,
            events=tuple(self.events),
        )

    def _reason_to_end(self) -> EndReason | None:
        if self.mario.pixel_y - SMALL_MARIO_HITBOX_OFFSET_Y_PIXELS >= PIT_DEATH_SPRITE_Y_PIXELS:
            return EndReason.FELL_IN_PIT
        if self.level_timer.has_run_out:
            return EndReason.TIMER_RAN_OUT
        if self._stall_rule is not None and self._stall_rule.has_stalled:
            return EndReason.STALLED
        return None
