"""Where training's and replay's buttons come from: a brain's answer, and a Controller log (#26)."""

import numpy as np
import pytest

from mario.controller.brain_controller_source import BrainControllerSource
from mario.controller.controller_bitmask import held_buttons_from_bitmasks
from mario.controller.controller_log_source import ControllerLogSource
from tests.game.helpers import HOLD_JUMP, HOLD_NOTHING, HOLD_RIGHT, HOLD_RIGHT_RUN


def test_a_controller_log_source_gives_back_the_logged_buttons_tick_by_tick():
    controller_log = np.array([HOLD_RIGHT, HOLD_RIGHT_RUN, HOLD_JUMP, HOLD_NOTHING], dtype=np.uint8)
    source = ControllerLogSource(controller_log)
    assert [source.next_buttons() for _ in range(len(controller_log))] == [
        HOLD_RIGHT, HOLD_RIGHT_RUN, HOLD_JUMP, HOLD_NOTHING]


def test_a_controller_log_source_refuses_to_go_past_the_end_of_its_log():
    source = ControllerLogSource(np.array([HOLD_RIGHT], dtype=np.uint8))
    source.next_buttons()
    with pytest.raises(IndexError):
        source.next_buttons()


def test_a_brains_answer_gives_agent_i_the_buttons_of_row_i():
    decisions = np.array([[False, True, False, False, True],    # right + run
                          [False, False, False, False, False],   # nothing
                          [False, False, False, True, False]])   # jump
    assert BrainControllerSource(agent_count=3).buttons_per_agent(decisions) == [
        HOLD_RIGHT_RUN, HOLD_NOTHING, HOLD_JUMP]


@pytest.mark.parametrize("decisions", [
    held_buttons_from_bitmasks(np.array([HOLD_RIGHT], dtype=np.uint8)),                         # one row too few
    held_buttons_from_bitmasks(np.array([HOLD_RIGHT, HOLD_RIGHT], dtype=np.uint8)).astype(float),  # not bools
    held_buttons_from_bitmasks(np.array([HOLD_RIGHT, HOLD_RIGHT], dtype=np.uint8))[:, :4],      # four buttons
    [[False, True, False, False, False]] * 2,                                                     # not an array
], ids=["one-row-too-few", "not-bools", "four-buttons", "a-list"])
def test_a_brain_must_answer_with_one_row_of_five_bools_per_agent(decisions):
    with pytest.raises(ValueError):
        BrainControllerSource(agent_count=2).buttons_per_agent(decisions)
