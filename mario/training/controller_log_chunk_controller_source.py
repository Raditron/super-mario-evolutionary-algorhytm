"""All-ghost replay's ChunkControllerSource: each agent of the chunk presses what his
Controller log recorded, tick after tick (spec section 11).

The worker pool, its ChunkPlayer and watch-live's snapshot pipeline play these
chunks exactly as they play training's, never knowing the buttons come from logs.
No algorithm is built and no genome is run, so all-ghost replay never imports
the user's neuroevolution package. The replayed attempts are training attempts,
stall rule on as when recorded, so each ends on the tick its recorded attempt
ended, as its log does.
"""

from collections.abc import Sequence

import numpy as np

from mario.controller.controller_log_source import ControllerLogSource
from mario.controller.controller_state import ControllerState
from mario.level.static_level import StaticLevel
from mario.simulation.attempt import Attempt
from mario.training.chunk_controller_source import ChunkControllerSource, ChunkControllerSourceFactory


class ControllerLogChunkControllerSource(ChunkControllerSource):
    def __init__(self, controller_logs: Sequence[np.ndarray]):
        self._controller_sources = [ControllerLogSource(controller_log) for controller_log in controller_logs]
        # An ended agent's buttons are never pressed, so he is left holding none.
        self._buttons_per_agent = [ControllerState.bitmask()] * len(controller_logs)

    def buttons_per_agent(self, attempts: Sequence[Attempt], living_agents: Sequence[int]) -> list[int]:
        for agent in living_agents:
            self._buttons_per_agent[agent] = self._controller_sources[agent].next_buttons()
        return self._buttons_per_agent


class ControllerLogChunkControllerSourceFactory(ChunkControllerSourceFactory):
    """What controls each agent is his Controller log; there is nothing to build in a worker."""

    def start_in_worker(self, level: StaticLevel) -> None:
        pass

    def for_chunk(self, agent_controls: Sequence[np.ndarray]) -> ChunkControllerSource:
        """agent_controls: the chunk's Controller logs, one uint8 bitmask per tick each."""
        return ControllerLogChunkControllerSource(agent_controls)
