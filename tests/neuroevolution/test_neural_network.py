"""Milestone 2: a network passes its input through every layer in order."""

import pytest

from tests.neuroevolution.tiny_networks import OUTPUT_A, OUTPUT_B, TINY_INPUTS, network_a, network_b


def test_a_tiny_network_matches_the_hand_calculation():
    assert network_a().forward(TINY_INPUTS) == pytest.approx([OUTPUT_A])


def test_another_tiny_network_matches_the_hand_calculation():
    assert network_b().forward(TINY_INPUTS) == pytest.approx([OUTPUT_B])


def test_the_output_has_the_shape_of_the_last_layer():
    assert network_a().forward(TINY_INPUTS).shape == (1,)
