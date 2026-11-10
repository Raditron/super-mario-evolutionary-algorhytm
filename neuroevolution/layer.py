"""Milestone 2: a layer, many neurons reading the same inputs."""

import numpy as np


class Layer:
    """weights has one row per input and one column per neuron; biases has one value per neuron."""

    def __init__(self, weights: np.ndarray, biases: np.ndarray) -> None:
        self._weights = weights
        self._biases = biases

    def forward(self, inputs: np.ndarray) -> np.ndarray:
        """The layer's outputs: tanh(inputs @ weights + biases)."""
        return np.tanh(inputs @ self._weights + self._biases)
            
