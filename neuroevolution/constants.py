"""Fixed facts the network is built around. They come from the game's seam, so they are never settings."""

from mario.constants.controller import CONTROLLER_BUTTONS
from mario.constants.observation import OBSERVATION_LENGTH

# The network reads one Observation and answers with one press-or-not per Controller button.
INPUT_SIZE = OBSERVATION_LENGTH
OUTPUT_SIZE = len(CONTROLLER_BUTTONS)
