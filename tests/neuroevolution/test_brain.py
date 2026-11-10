"""Milestone 2: a Brain decides for every agent at once, row i for agent i."""

import numpy as np
import pytest

from neuroevolution.brain import Brain
from tests.neuroevolution.tiny_networks import TINY_INPUTS, network_a, network_b

PRESS_EVERYTHING_THRESHOLD = 0.0
# Between network A's output (0.47) and network B's (0.75).
BETWEEN_THE_TWO_OUTPUTS_THRESHOLD = 0.6
TWO_AGENTS_SAME_OBSERVATION = np.array([TINY_INPUTS, TINY_INPUTS])


def test_the_presses_are_one_bool_row_per_agent():
    brain = Brain([network_a(), network_b()], PRESS_EVERYTHING_THRESHOLD)

    presses = brain.decide(TWO_AGENTS_SAME_OBSERVATION)

    assert presses.shape == (2, 1)
    assert presses.dtype == np.bool_


def test_a_button_is_pressed_when_its_output_is_above_the_threshold():
    brain = Brain([network_a(), network_b()], BETWEEN_THE_TWO_OUTPUTS_THRESHOLD)

    presses = brain.decide(TWO_AGENTS_SAME_OBSERVATION)

    assert presses.tolist() == [[False], [True]]


def test_row_i_is_decided_by_network_i():
    brain = Brain([network_b(), network_a()], BETWEEN_THE_TWO_OUTPUTS_THRESHOLD)

    presses = brain.decide(TWO_AGENTS_SAME_OBSERVATION)

    assert presses.tolist() == [[True], [False]]


def test_the_brain_gives_the_same_presses_as_each_network_on_its_own():
    networks = [network_a(), network_b()]
    brain = Brain(networks, BETWEEN_THE_TWO_OUTPUTS_THRESHOLD)

    presses = brain.decide(TWO_AGENTS_SAME_OBSERVATION)

    for agent_index, network in enumerate(networks):
        on_its_own = network.forward(TINY_INPUTS) > BETWEEN_THE_TWO_OUTPUTS_THRESHOLD
        assert presses[agent_index].tolist() == on_its_own.tolist()


def test_observations_for_the_wrong_number_of_agents_are_refused():
    brain = Brain([network_a(), network_b()], PRESS_EVERYTHING_THRESHOLD)

    with pytest.raises(ValueError, match="agents"):
        brain.decide(np.array([TINY_INPUTS]))
