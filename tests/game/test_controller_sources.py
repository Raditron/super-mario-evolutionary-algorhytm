"""Where training's and replay's buttons come from: a Controller log, and a brain (#26)."""

import numpy as np
import pytest

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
