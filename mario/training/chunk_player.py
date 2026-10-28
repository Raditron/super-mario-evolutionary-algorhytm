"""A chunk of agents plays its training attempts in lock-step.

Every tick, the chunk's ChunkControllerSource gives each living agent his
buttons (in training, a brain decides for the whole chunk at once), and each
living agent's Attempt steps with his own. Training attempts have the stall
rule on. A watched chunk also has a tick listener, told after every tick (spec
section 11); headless, there is none, and the lock-step does nothing more.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

import numpy as np

from mario.level.static_level import StaticLevel
from mario.simulation.attempt import Attempt
from mario.simulation.attempt_result import AttemptResult
from mario.training.chunk_controller_source import ChunkControllerSource


@dataclass(frozen=True)
class PlayedAttempt:
    """One agent's finished attempt: its result, and its Controller log (one uint8 bitmask per tick)."""
    attempt_result: AttemptResult
    controller_log: np.ndarray


class ChunkTickListener(Protocol):
    def tick_played(self, attempts: Sequence[Attempt]) -> None:
        """Every attempt of the chunk, ended or not, once it has played a tick; read only."""


class ChunkPlayer:
    def __init__(self, level: StaticLevel):
        self._level = level

    def play(self, controller_source: ChunkControllerSource, agent_count: int,
             tick_listener: ChunkTickListener | None = None) -> list[PlayedAttempt]:
        """Play one training attempt per agent, all in lock-step, until every one has ended."""
        attempts = [Attempt(self._level, ends_on_stall=True) for _ in range(agent_count)]
        controller_logs = [bytearray() for _ in range(agent_count)]
        living_agents = list(range(agent_count))
        while living_agents:
            buttons_per_agent = controller_source.buttons_per_agent(attempts, living_agents)
            for agent in living_agents:
                attempts[agent].step(buttons_per_agent[agent])
                controller_logs[agent].append(buttons_per_agent[agent])
            living_agents = [agent for agent in living_agents if not attempts[agent].is_over]
            if tick_listener is not None:
                tick_listener.tick_played(attempts)
        return [PlayedAttempt(attempt.result(), np.frombuffer(bytes(controller_log), dtype=np.uint8))
                for attempt, controller_log in zip(attempts, controller_logs)]
