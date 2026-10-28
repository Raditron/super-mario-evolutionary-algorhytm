"""Which agent is a generation's best (spec section 10): the one rule that both
recording the best genome and replaying the best agent go by."""

from collections.abc import Sequence

import numpy as np


def best_agent_index(fitnesses: Sequence[float] | np.ndarray) -> int:
    """fitnesses: one per agent, by agent index. The agent with the highest fitness;
    on a tie, the lowest index (argmax returns the first)."""
    return int(np.argmax(fitnesses))
