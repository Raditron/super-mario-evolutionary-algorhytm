"""Milestone 2: a layer is tanh(inputs @ weights + biases)."""

import numpy as np
import pytest

from neuroevolution.layer import Layer
from tests.neuroevolution.tiny_networks import HIDDEN_SUMS_A, TINY_INPUTS, hidden_layer_a


def test_a_layer_matches_the_hand_calculation():
    assert hidden_layer_a().forward(TINY_INPUTS) == pytest.approx(np.tanh(HIDDEN_SUMS_A))


def test_a_layer_gives_one_output_per_neuron():
    assert hidden_layer_a().forward(TINY_INPUTS).shape == (2,)


def test_all_zero_weights_and_biases_give_zeros():
    layer = Layer(np.zeros((2, 3)), np.zeros(3))

    assert layer.forward(TINY_INPUTS) == pytest.approx(np.zeros(3))


def test_a_layer_reads_a_row_per_agent():
    two_agents = np.array([TINY_INPUTS, TINY_INPUTS])

    outputs = hidden_layer_a().forward(two_agents)

    assert outputs.shape == (2, 2)
    assert outputs[1] == pytest.approx(hidden_layer_a().forward(TINY_INPUTS))
