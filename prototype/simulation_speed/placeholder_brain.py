"""COST PLACEHOLDER ONLY. This is NOT the user's neural network or genetic algorithm.

Per CLAUDE.md the learning algorithm is written by the user. This module only
burns a realistic amount of CPU per decision (156 -> 24 tanh -> 4 matmuls on
random weights) so the timing in issue #4 means something. It never learns.
"""

import numpy as np

from . import constants as c

INPUT_SIZE = c.OBSERVATION_SIZE
HIDDEN_SIZE = c.PLACEHOLDER_HIDDEN_SIZE
OUTPUT_SIZE = c.PLACEHOLDER_OUTPUT_SIZE
FIRST_LAYER_WEIGHTS_END = INPUT_SIZE * HIDDEN_SIZE
FIRST_LAYER_BIASES_END = FIRST_LAYER_WEIGHTS_END + HIDDEN_SIZE
SECOND_LAYER_WEIGHTS_END = FIRST_LAYER_BIASES_END + HIDDEN_SIZE * OUTPUT_SIZE
PARAMETER_COUNT = SECOND_LAYER_WEIGHTS_END + OUTPUT_SIZE
BUTTON_VALUES = np.array(c.CONTROLLER_BUTTON_ORDER, dtype=np.int64)
RIGHT_OUTPUT_INDEX = c.CONTROLLER_BUTTON_ORDER.index(c.BUTTON_RIGHT)


def random_placeholder_parameters(agent_count: int, rng: np.random.Generator) -> np.ndarray:
    """(agent_count, PARAMETER_COUNT) random weights, biased to press right."""
    parameters = rng.normal(0.0, c.PLACEHOLDER_WEIGHT_SCALE, size=(agent_count, PARAMETER_COUNT))
    parameters[:, SECOND_LAYER_WEIGHTS_END + RIGHT_OUTPUT_INDEX] += c.PLACEHOLDER_RIGHT_BIAS
    return parameters


def _split_layers(parameters: np.ndarray):
    """Views of the flat parameter vector(s) as (w1, b1, w2, b2); works on 1-D or 2-D."""
    leading = parameters.shape[:-1]
    first_weights = parameters[..., :FIRST_LAYER_WEIGHTS_END].reshape(*leading, INPUT_SIZE, HIDDEN_SIZE)
    first_biases = parameters[..., FIRST_LAYER_WEIGHTS_END:FIRST_LAYER_BIASES_END]
    second_weights = parameters[..., FIRST_LAYER_BIASES_END:SECOND_LAYER_WEIGHTS_END].reshape(
        *leading, HIDDEN_SIZE, OUTPUT_SIZE)
    second_biases = parameters[..., SECOND_LAYER_WEIGHTS_END:]
    return first_weights, first_biases, second_weights, second_biases


class PlaceholderBrain:
    """One agent's stand-in brain, asked one observation at a time."""

    def __init__(self, parameters: np.ndarray):
        layers = _split_layers(np.ascontiguousarray(parameters))
        self.first_weights, self.first_biases, self.second_weights, self.second_biases = layers

    def choose_buttons(self, observation: np.ndarray) -> int:
        hidden = np.tanh(observation @ self.first_weights + self.first_biases)
        outputs = hidden @ self.second_weights + self.second_biases
        return int(BUTTON_VALUES[outputs > c.PLACEHOLDER_PRESS_THRESHOLD].sum())


class PlaceholderBrainBatch:
    """Many agents' stand-in brains evaluated in one stacked matmul (one row per agent)."""

    def __init__(self, parameters: np.ndarray):
        self._load(np.ascontiguousarray(parameters))

    def _load(self, parameters: np.ndarray) -> None:
        self.parameters = parameters
        layers = _split_layers(parameters)
        first_weights, self.first_biases, second_weights, self.second_biases = layers
        self.first_weights = np.ascontiguousarray(first_weights)
        self.second_weights = np.ascontiguousarray(second_weights)

    @property
    def row_count(self) -> int:
        return self.parameters.shape[0]

    def keep_rows(self, rows: np.ndarray) -> None:
        """Drop finished agents so later ticks stop paying for them."""
        self._load(self.parameters[rows])

    def choose_buttons(self, observations: np.ndarray) -> np.ndarray:
        """observations: (row_count, INPUT_SIZE) -> Controller bitmask per row."""
        hidden = np.tanh(np.matmul(observations[:, None, :], self.first_weights)[:, 0, :]
                         + self.first_biases)
        outputs = np.matmul(hidden[:, None, :], self.second_weights)[:, 0, :] + self.second_biases
        return (outputs > c.PLACEHOLDER_PRESS_THRESHOLD) @ BUTTON_VALUES
