"""Training's Controller: a brain presses the buttons for a chunk of agents in lock-step.

Every tick, the living agents' Observations are built as one batch, the brain
decides for the whole chunk at once, and each living agent's Attempt steps with
its own buttons. Training attempts have the stall rule on.
"""

from dataclasses import dataclass

import numpy as np

from mario.constants.controller import CONTROLLER_BUTTONS
from mario.constants.observation import OBSERVATION_LENGTH
from mario.level.static_level import StaticLevel
from mario.simulation.attempt import Attempt
from mario.simulation.attempt_result import AttemptResult
from mario.simulation.observation_builder import ObservationBuilder
from mario.training.neuroevolution_algorithm import Brain

# Each decision column's bit in the Controller bitmask, in Controller order.
BUTTON_BITS = np.array([1 << bit for bit in range(len(CONTROLLER_BUTTONS))], dtype=np.uint8)


@dataclass(frozen=True)
class PlayedAttempt:
    """One agent's finished attempt: its result, and its Controller log (one uint8 bitmask per tick)."""
    attempt_result: AttemptResult
    controller_log: np.ndarray


class BrainControllerSource:
    def __init__(self, level: StaticLevel):
        self._level = level
        self._observation_builder = ObservationBuilder(level)

    def play(self, brain: Brain, agent_count: int) -> list[PlayedAttempt]:
        """Play one training attempt per agent, all in lock-step, until every one has ended."""
        attempts = [Attempt(self._level, ends_on_stall=True) for _ in range(agent_count)]
        controller_logs = [bytearray() for _ in range(agent_count)]
        observations = np.empty((agent_count, OBSERVATION_LENGTH), dtype=np.float64)
        living_agents = list(range(agent_count))
        while living_agents:
            observations[living_agents] = self._observation_builder.build_batch(
                [attempts[agent] for agent in living_agents])
            buttons_per_agent = self._buttons_from(brain.decide(observations), agent_count)
            for agent in living_agents:
                attempts[agent].step(buttons_per_agent[agent])
                controller_logs[agent].append(buttons_per_agent[agent])
            living_agents = [agent for agent in living_agents if not attempts[agent].is_over]
        return [PlayedAttempt(attempt.result(), np.frombuffer(bytes(controller_log), dtype=np.uint8))
                for attempt, controller_log in zip(attempts, controller_logs)]

    @staticmethod
    def _buttons_from(decisions: np.ndarray, agent_count: int) -> list[int]:
        """Each agent's Controller bitmask from the brain's (agents x 5) bools."""
        expected_shape = (agent_count, len(CONTROLLER_BUTTONS))
        if not isinstance(decisions, np.ndarray) or decisions.dtype != np.bool_ or decisions.shape != expected_shape:
            raise ValueError(f"a brain must decide with a {expected_shape} bool array, "
                             f"got {getattr(decisions, 'dtype', type(decisions))} "
                             f"{getattr(decisions, 'shape', '')}")
        return (decisions @ BUTTON_BITS).tolist()
