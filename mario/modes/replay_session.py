"""One recorded attempt played again from its Controller log (best-agent replay, spec section 11).

The attempt is rebuilt tick by tick from the buttons the log recorded, never by
re-running a genome. The recorded attempts are training attempts, so the stall
rule is on, as it was when they were recorded, and the replay ends where the
recorded attempt ended. One that reached the flag then plays out the end of the
level, input-free (Attempt.step_end_of_level), as play mode does. Once over, the
replay holds still.
"""

import numpy as np

from mario.controller.controller_log_source import ControllerLogSource
from mario.level.static_level import StaticLevel
from mario.simulation.attempt import Attempt
from mario.simulation.attempt_result import EndReason
from mario.simulation.observation_builder import ObservationBuilder
from mario.snapshots.world_snapshot import WorldSnapshot


class ReplaySession:
    def __init__(self, controller_log: np.ndarray, level: StaticLevel):
        """controller_log: one uint8 Controller bitmask per tick of the recorded attempt."""
        self._controller_source = ControllerLogSource(controller_log)
        self._observation_builder = ObservationBuilder(level)
        self.attempt = Attempt(level, ends_on_stall=True)

    @property
    def is_finished(self) -> bool:
        """The recorded attempt has ended, and so has the end of the level if it reached the flag."""
        if self.attempt.end_reason is EndReason.REACHED_FLAG:
            return self.attempt.end_of_level.is_over
        return self.attempt.is_over

    def step(self) -> None:
        """One tick of the recorded attempt, the next of the end of the level
        (from the touch's own tick on), or nothing once the replay is finished."""
        if not self.attempt.is_over:
            self.attempt.step(self._controller_source.next_buttons())
        if self.attempt.end_reason is EndReason.REACHED_FLAG and not self.is_finished:
            self.attempt.step_end_of_level()

    def snapshot(self) -> WorldSnapshot:
        return WorldSnapshot.of(self.attempt, observation_builder=self._observation_builder)
