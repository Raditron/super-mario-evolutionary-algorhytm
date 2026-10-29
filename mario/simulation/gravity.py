"""The original's ImposeGravity speed update, shared by Mario and enemies."""

from mario.constants.physics import FALL_CAP_FRACTION_THRESHOLD, Y_SUBSPEED_MASK


def whole_speed_y(velocity_y: int) -> int:
    """The part of a y speed that moves its body (the speed byte); the fraction only carries into it."""
    return velocity_y - (velocity_y & Y_SUBSPEED_MASK)


def add_gravity(velocity_y: int, gravity: int, terminal_fall_speed: int) -> int:
    """The fall speed after one tick of gravity. It is clamped to the terminal
    speed only once its fraction reaches half a pixel, so it can overshoot for a tick."""
    velocity_y += gravity
    fraction_reaches_fall_cap_threshold = (velocity_y & Y_SUBSPEED_MASK) >= FALL_CAP_FRACTION_THRESHOLD
    if whole_speed_y(velocity_y) >= terminal_fall_speed and fraction_reaches_fall_cap_threshold:
        return terminal_fall_speed
    return velocity_y
