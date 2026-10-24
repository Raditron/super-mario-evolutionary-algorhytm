import pytest

from mario.constants.controller import CONTROLLER_BUTTONS
from mario.controller.controller_state import LEFT, NO_DIRECTION, RIGHT, ControllerState


def test_buttons_use_bits_0_to_4_in_controller_order():
    assert CONTROLLER_BUTTONS == ("left", "right", "down", "jump", "run")
    assert [ControllerState.bitmask(**{button: True}) for button in CONTROLLER_BUTTONS] == [1, 2, 4, 8, 16]


def test_one_direction_held_gives_that_direction():
    assert ControllerState(ControllerState.bitmask(left=True)).direction == LEFT
    assert ControllerState(ControllerState.bitmask(right=True)).direction == RIGHT


def test_left_and_right_held_together_count_as_neither():
    both = ControllerState(ControllerState.bitmask(left=True, right=True))
    assert both.direction == NO_DIRECTION
    assert not both.holds_any_button_but_jump


def test_a_value_outside_the_five_bits_is_rejected():
    with pytest.raises(ValueError):
        ControllerState(1 << len(CONTROLLER_BUTTONS))
