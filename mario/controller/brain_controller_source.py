"""Training's Controller: a brain's answer for one tick becomes each agent's Controller bitmask."""

import numpy as np

from mario.constants.controller import CONTROLLER_BUTTONS
from mario.controller.controller_bitmask import bitmasks_from_held_buttons


class BrainControllerSource:
    """The Controller of a chunk of agents, all pressed by one brain at once."""

    def __init__(self, agent_count: int):
        self._expected_shape = (agent_count, len(CONTROLLER_BUTTONS))

    def buttons_per_agent(self, decisions: np.ndarray) -> list[int]:
        """Each agent's Controller bitmask from the brain's (agents x 5) bools, row i for agent i."""
        if (not isinstance(decisions, np.ndarray) or decisions.dtype != np.bool_
                or decisions.shape != self._expected_shape):
            raise ValueError(f"a brain must decide with a {self._expected_shape} bool array, "
                             f"got {getattr(decisions, 'dtype', type(decisions))} "
                             f"{getattr(decisions, 'shape', '')}")
        return bitmasks_from_held_buttons(decisions).tolist()
