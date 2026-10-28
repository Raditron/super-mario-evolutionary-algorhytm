"""After the flagpole touch, in play mode (#24, spec section 5): the flag slide, the
castle walk and the timer counting down into the score play out with no input,
then a new game starts."""

from mario.constants.level import SCREEN_WIDTH_PIXELS, SCROLL_STOP_LEFT_X_PIXELS, TILE_SIZE_PIXELS
from mario.constants.scoring import STARTING_LIVES
from mario.modes.play_session import PlaySession
from mario.simulation.attempt_result import EndReason
from mario.snapshots.world_snapshot import WorldSnapshot
from tests.game.helpers import CASTLE_STOPPER_X_PIXELS, HOLD_LEFT, PILOT_ENEMY_LOOK_AHEAD_PIXELS
from tests.game.scripted_pilot import ScriptedPilot

FLAGPOLE_X_PIXELS = 198 * TILE_SIZE_PIXELS
CASTLE_RIGHT_X_PIXELS = 207 * TILE_SIZE_PIXELS
# 1-1's flag hangs left of the pole with its top at y = 48 (FlagpoleObject); the
# slide ends once it is down at y = 170 ($AA, FlagpoleRoutine).
FLAG_X_PIXELS = FLAGPOLE_X_PIXELS - 8
FLAG_START_Y_PIXELS = 48
FLAG_BOTTOM_Y_PIXELS = 170
# Holding the pole, Mario's sprite is 7 px left of its column, so his box 5 px (PutPlayerOnVine).
MARIO_ON_THE_POLE_X_PIXELS = FLAGPOLE_X_PIXELS - 5
POINTS_PER_TIME_UNIT_LEFT = 50


def run_to_the_flagpole(session: PlaySession):
    """Play 1-1 until Mario touches the pole; return that attempt."""
    attempt = session.attempt
    pilot = ScriptedPilot(PILOT_ENEMY_LOOK_AHEAD_PIXELS)
    while not attempt.is_over:
        session.step(pilot.next_buttons(attempt))
    assert attempt.end_reason is EndReason.REACHED_FLAG
    return attempt


def play_out_the_end_of_the_level(session: PlaySession) -> list[WorldSnapshot]:
    """Step, pressing left all along, until the next game starts; return a snapshot of every tick before it."""
    finished_attempt = session.attempt
    snapshots = []
    while True:
        session.step(HOLD_LEFT)
        if session.attempt is not finished_attempt:
            return snapshots
        snapshots.append(session.snapshot())


def test_in_play_mode_the_slide_and_castle_walk_play_out_then_a_new_game_starts(world_1_1):
    session = PlaySession(world_1_1)
    attempt = run_to_the_flagpole(session)
    final_score = attempt.result().final_score
    time_left_at_the_touch = attempt.level_timer.time_left
    score_before_the_touch = final_score - attempt.flagpole_touch.flag_points - (
        POINTS_PER_TIME_UNIT_LEFT * time_left_at_the_touch)
    snapshots = play_out_the_end_of_the_level(session)

    flag_heights = [snapshot.flag.y_pixels for snapshot in snapshots]
    assert {snapshot.flag.x_pixels for snapshot in snapshots} == {FLAG_X_PIXELS}
    assert flag_heights == sorted(flag_heights)
    assert FLAG_START_Y_PIXELS < flag_heights[0] and flag_heights[-1] >= FLAG_BOTTOM_Y_PIXELS
    slide = [snapshot for snapshot in snapshots if snapshot.flag.y_pixels < FLAG_BOTTOM_Y_PIXELS]
    assert {snapshot.mario.x_pixels for snapshot in slide} == {MARIO_ON_THE_POLE_X_PIXELS}
    mario_heights = [snapshot.mario.y_pixels for snapshot in slide]
    assert mario_heights == sorted(mario_heights) and mario_heights[-1] > mario_heights[0]
    assert {(snapshot.hud.score, snapshot.hud.time_left) for snapshot in slide} == {
        (score_before_the_touch, time_left_at_the_touch)}

    last = snapshots[-1]
    assert last.mario.x_pixels + last.mario.width_pixels == CASTLE_STOPPER_X_PIXELS
    assert (last.hud.score, last.hud.time_left) == (final_score, 0)
    counting = [snapshot.hud for snapshot in snapshots if snapshot.hud.time_left < time_left_at_the_touch]
    assert [hud.time_left for hud in counting] == list(range(time_left_at_the_touch - 1, -1, -1))
    assert [final_score - hud.score for hud in counting] == [POINTS_PER_TIME_UNIT_LEFT * hud.time_left
                                                             for hud in counting]

    screen_left_edges = [snapshot.screen_left_x_pixels for snapshot in snapshots]
    assert screen_left_edges == sorted(screen_left_edges)
    assert screen_left_edges[-1] == SCROLL_STOP_LEFT_X_PIXELS
    assert CASTLE_RIGHT_X_PIXELS - SCREEN_WIDTH_PIXELS <= SCROLL_STOP_LEFT_X_PIXELS < FLAG_X_PIXELS

    assert (session.attempt.ticks_elapsed, session.score, session.lives) == (0, 0, STARTING_LIVES)
