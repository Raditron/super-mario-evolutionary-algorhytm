"""Milestone 2: layers in a row, each reading the one before."""

import numpy as np

from neuroevolution.layer import Layer


class NeuralNetwork:
    def __init__(self, layers: list[Layer]) -> None:
        self._layers = layers

    def forward(self, observations: np.ndarray) -> np.ndarray:
        """The network's outputs: the observations passed through every layer in order."""
        signal = observations
        for layer in self._layers: 
            signal = layer.forward(signal)
        return signal    
