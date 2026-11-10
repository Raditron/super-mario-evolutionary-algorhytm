"""Milestone 1: one neuron. A learning step that milestone 2 replaces with matrix maths."""

import numpy as np


def neuron_output(inputs: np.ndarray, weights: np.ndarray, bias: float) -> float:
    """The neuron's output: tanh of the weighted sum of its inputs plus the bias."""
    result: float = 0
    for input, weight in zip(inputs, weights):
        result += float(input) * float(weight)
    result += bias
    return float(np.tanh(result))
