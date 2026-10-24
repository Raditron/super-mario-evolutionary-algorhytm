"""The original's ImposeGravity speed update, shared by Mario and enemies."""

from mario.constants.physics import FALL_CAP_FRACTION_THRESHOLD, Y_SUBSPEED_MASK


def add_gravity(velocity_y: int, gravity: int, terminal_fall_speed: int) -> int:
    """The fall speed after one tick of gravity. It is clamped to the terminal
    speed only once its fraction reaches half a pixel, so it can overshoot for a tick."""
    velocity_y += gravity
    whole_speed_y = velocity_y - (velocity_y & Y_SUBSPEED_MASK)
    if whole_speed_y >= terminal_fall_speed and (velocity_y & Y_SUBSPEED_MASK) >= FALL_CAP_FRACTION_THRESHOLD:
        return terminal_fall_speed
    return velocity_y
