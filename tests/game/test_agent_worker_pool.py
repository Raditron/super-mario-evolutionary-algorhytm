"""The worker pool plays whatever controls its agents, through one seam: a ChunkControllerSourceFactory
(spec sections 9 and 11). Training's is the brain built from genomes; all-ghost replay (#30) is to
bring one of Controller logs, with no algorithm built."""

from mario.simulation.attempt import Attempt
from mario.simulation.attempt_result import EndReason
from mario.training.agent_worker_pool import AgentWorkerPool
from tests.game.chunk_controller_source_doubles import FixedButtonsControllerSourceFactory
from tests.game.helpers import HOLD_JUMP, HOLD_NOTHING, HOLD_RIGHT

WORKER_COUNT = 2
GENERATION = 1


def hand_played(level, buttons: int):
    """A training attempt (stall rule on) holding the same buttons until it ends."""
    attempt = Attempt(level, ends_on_stall=True)
    while not attempt.is_over:
        attempt.step(buttons)
    return attempt.result()


def test_the_pool_plays_agents_whose_buttons_come_from_no_brain(world_1_1):
    held_buttons = [HOLD_RIGHT, HOLD_NOTHING, HOLD_JUMP, HOLD_RIGHT, HOLD_NOTHING]
    with AgentWorkerPool(FixedButtonsControllerSourceFactory(), WORKER_COUNT) as worker_pool:
        played_attempts = worker_pool.play(held_buttons, GENERATION)
    assert [played.attempt_result for played in played_attempts] == [
        hand_played(world_1_1, buttons) for buttons in held_buttons]
    assert [set(played.controller_log.tolist()) for played in played_attempts] == [
        {buttons} for buttons in held_buttons]
    assert played_attempts[1].attempt_result.end_reason == EndReason.STALLED
