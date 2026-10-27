"""A chunk of agents plays its training attempts in lock-step under one brain (#26, spec section 9)."""

import numpy as np
import pytest

from mario.constants.training import STALL_LIMIT_TICKS
from mario.controller.controller_bitmask import held_buttons_from_bitmasks
from mario.simulation.attempt import Attempt
from mario.simulation.attempt_result import EndReason
from mario.training.chunk_player import ChunkPlayer
from tests.game.helpers import HOLD_JUMP, HOLD_NOTHING, HOLD_RIGHT_RUN, build_level

OBSERVATION_LENGTH = 160          # spec section 7
PIT_AHEAD_OF_THE_SPAWN = range(10, 14)


class FixedButtonsBrain:
    """A brain whose agent i holds the same buttons every tick. It keeps every batch it is shown."""

    def __init__(self, buttons_per_agent: list[int]):
        self._decisions = held_buttons_from_bitmasks(np.array(buttons_per_agent, dtype=np.uint8))
        self.observation_batches: list[np.ndarray] = []

    def decide(self, observations: np.ndarray) -> np.ndarray:
        self.observation_batches.append(observations.copy())
        return self._decisions.copy()


def hand_played(level, buttons: int):
    """A training attempt (stall rule on) holding the same buttons until it ends."""
    attempt = Attempt(level, ends_on_stall=True)
    while not attempt.is_over:
        attempt.step(buttons)
    return attempt.result()


@pytest.fixture
def level_with_a_pit():
    return build_level(pit_columns=PIT_AHEAD_OF_THE_SPAWN)


def test_a_brain_plays_each_agent_of_a_chunk_to_the_end_of_its_own_training_attempt(level_with_a_pit):
    brain = FixedButtonsBrain([HOLD_RIGHT_RUN, HOLD_NOTHING])
    runner, idler = ChunkPlayer(level_with_a_pit).play(brain, agent_count=2)
    assert runner.attempt_result == hand_played(level_with_a_pit, HOLD_RIGHT_RUN)
    assert runner.attempt_result.end_reason == EndReason.FELL_IN_PIT
    assert idler.attempt_result == hand_played(level_with_a_pit, HOLD_NOTHING)
    assert idler.attempt_result.end_reason == EndReason.STALLED


def test_each_agent_gets_a_controller_log_of_one_uint8_bitmask_per_tick(level_with_a_pit):
    brain = FixedButtonsBrain([HOLD_RIGHT_RUN, HOLD_JUMP])
    runner, jumper = ChunkPlayer(level_with_a_pit).play(brain, agent_count=2)
    assert runner.controller_log.dtype == np.uint8
    assert runner.controller_log.tolist() == [HOLD_RIGHT_RUN] * runner.attempt_result.ticks_elapsed
    assert jumper.controller_log.tolist() == [HOLD_JUMP] * STALL_LIMIT_TICKS


def test_the_brain_sees_one_observation_row_per_agent_of_the_chunk_until_the_last_attempt_ends(
        level_with_a_pit):
    brain = FixedButtonsBrain([HOLD_RIGHT_RUN, HOLD_NOTHING])
    runner, idler = ChunkPlayer(level_with_a_pit).play(brain, agent_count=2)
    assert runner.attempt_result.ticks_elapsed < idler.attempt_result.ticks_elapsed
    assert len(brain.observation_batches) == idler.attempt_result.ticks_elapsed
    assert {(batch.shape, batch.dtype) for batch in brain.observation_batches} == {
        ((2, OBSERVATION_LENGTH), np.dtype(np.float64))}


def test_an_agent_whose_attempt_has_ended_keeps_showing_its_last_observation(level_with_a_pit):
    brain = FixedButtonsBrain([HOLD_RIGHT_RUN, HOLD_NOTHING])
    runner, _ = ChunkPlayer(level_with_a_pit).play(brain, agent_count=2)
    last_decision = runner.attempt_result.ticks_elapsed - 1
    last_observation = brain.observation_batches[last_decision][0]
    assert all(np.array_equal(batch[0], last_observation)
               for batch in brain.observation_batches[last_decision:])


def test_a_brain_that_answers_wrongly_stops_the_chunk(level_with_a_pit):
    class OneRowTooFew(FixedButtonsBrain):
        def decide(self, observations):
            return super().decide(observations)[1:]

    with pytest.raises(ValueError):
        ChunkPlayer(level_with_a_pit).play(OneRowTooFew([HOLD_RIGHT_RUN, HOLD_RIGHT_RUN]), agent_count=2)
