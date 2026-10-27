"""A chunk of agents plays its training attempts in lock-step under one brain.

Every tick, the living agents' Observations are built as one batch, the brain
decides for the whole chunk at once, and each living agent's Attempt steps with
its own buttons. Training attempts have the stall rule on.
"""

from dataclasses import dataclass

import numpy as np

from mario.constants.observation import OBSERVATION_LENGTH
from mario.controller.brain_controller_source import BrainControllerSource
from mario.level.static_level import StaticLevel
from mario.simulation.attempt import Attempt
from mario.simulation.attempt_result import AttemptResult
from mario.simulation.observation_builder import ObservationBuilder
from mario.training.neuroevolution_algorithm import Brain


@dataclass(frozen=True)
class PlayedAttempt:
    """One agent's finished attempt: its result, and its Controller log (one uint8 bitmask per tick)."""
    attempt_result: AttemptResult
    controller_log: np.ndarray


class ChunkPlayer:
    def __init__(self, level: StaticLevel):
        self._level = level
        self._observation_builder = ObservationBuilder(level)

    def play(self, brain: Brain, agent_count: int) -> list[PlayedAttempt]:
        """Play one training attempt per agent, all in lock-step, until every one has ended.

        The brain gets one row per agent every tick; an ended agent's row keeps
        its last Observation, and its answer is ignored."""
        attempts = [Attempt(self._level, ends_on_stall=True) for _ in range(agent_count)]
        controller_source = BrainControllerSource(agent_count)
        controller_logs = [bytearray() for _ in range(agent_count)]
        observations = np.empty((agent_count, OBSERVATION_LENGTH), dtype=np.float64)
        living_agents = list(range(agent_count))
        while living_agents:
            observations[living_agents] = self._observation_builder.build_batch(
                [attempts[agent] for agent in living_agents])
            buttons_per_agent = controller_source.buttons_per_agent(brain.decide(observations))
            for agent in living_agents:
                attempts[agent].step(buttons_per_agent[agent])
                controller_logs[agent].append(buttons_per_agent[agent])
            living_agents = [agent for agent in living_agents if not attempts[agent].is_over]
        return [PlayedAttempt(attempt.result(), np.frombuffer(bytes(controller_log), dtype=np.uint8))
                for attempt, controller_log in zip(attempts, controller_logs)]
