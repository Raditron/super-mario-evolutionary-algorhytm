"""Milestone 2: what build_brain returns, the game's Brain protocol (spec section 9)."""

import numpy as np

from neuroevolution.neural_network import NeuralNetwork


class Brain:
    """Agent i is decided for by networks[i]: row i of the observations, row i of the presses."""

    def __init__(self, networks: list[NeuralNetwork], button_press_threshold: float) -> None:
        self._networks = networks
        self._button_press_threshold = button_press_threshold
    
    def decide(self, observations: np.ndarray) -> np.ndarray:
        """(agents x inputs) float64 -> (agents x buttons) bool: a button is pressed when its output is above the threshold."""
        if len(observations) != len(self._networks):
            raise ValueError(f"{len(observations)} Observations for {len(self._networks)} agents")
        outputs = [network.forward(observation) for network, observation in zip(self._networks, observations)]
        return np.array(outputs) > self._button_press_threshold

