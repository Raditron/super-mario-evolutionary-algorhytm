"""Milestone 1: a neuron computes tanh(w . x + b)."""

import numpy as np
import pytest

from neuroevolution.neuron import neuron_output

# Worked out on paper: z = 1*0.5 + 2*(-1) + 3*0.25 + 0.5 = -0.25, and tanh(-0.25) = -0.2449186624...
HAND_INPUTS = np.array([1.0, 2.0, 3.0])
HAND_WEIGHTS = np.array([0.5, -1.0, 0.25])
HAND_BIAS = 0.5
HAND_OUTPUT = -0.2449186624037092

# A weighted sum this far from 0 leaves tanh saturated at its limit.
LARGE_INPUT = 1000.0
SATURATED_OUTPUT = 1.0


def test_all_zero_weights_and_bias_give_zero():
    assert neuron_output(HAND_INPUTS, np.zeros(len(HAND_INPUTS)), 0.0) == 0.0


def test_a_known_three_input_case_matches_the_hand_calculation():
    assert neuron_output(HAND_INPUTS, HAND_WEIGHTS, HAND_BIAS) == pytest.approx(HAND_OUTPUT)


def test_the_output_is_one_float():
    assert isinstance(neuron_output(HAND_INPUTS, HAND_WEIGHTS, HAND_BIAS), float)


def test_a_very_large_sum_saturates_at_one():
    assert neuron_output(np.array([LARGE_INPUT]), np.array([1.0]), 0.0) == pytest.approx(SATURATED_OUTPUT)


def test_a_very_negative_sum_saturates_at_minus_one():
    assert neuron_output(np.array([LARGE_INPUT]), np.array([-1.0]), 0.0) == pytest.approx(-SATURATED_OUTPUT)
