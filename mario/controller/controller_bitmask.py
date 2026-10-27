"""The one rule between a row of held buttons and a Controller bitmask.

A row is five bools in Controller order (CONTROLLER_BUTTONS), the way a brain
answers; button k of the row is bit k of the bitmask.
"""

import numpy as np

from mario.constants.controller import CONTROLLER_BUTTONS

# Each button's bit in the Controller bitmask, in Controller order.
BUTTON_BITS = np.array([1 << bit for bit in range(len(CONTROLLER_BUTTONS))], dtype=np.uint8)


def bitmasks_from_held_buttons(held_buttons: np.ndarray) -> np.ndarray:
    """(rows x 5) bools -> one uint8 Controller bitmask per row."""
    return held_buttons @ BUTTON_BITS


def held_buttons_from_bitmasks(bitmasks: np.ndarray) -> np.ndarray:
    """One Controller bitmask per row -> (rows x 5) bools."""
    return (np.asarray(bitmasks, dtype=np.uint8)[:, None] & BUTTON_BITS) != 0
