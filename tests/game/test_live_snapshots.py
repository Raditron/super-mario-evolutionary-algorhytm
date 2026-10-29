"""What watch-live's snapshots hold, and which agents the window follows and draws as ghosts (#29, spec sections 8 and 11)."""

from dataclasses import replace

from mario.constants.view import GHOST_DRAW_LIMIT
from mario.level.static_level import StaticLevel
from mario.simulation.attempt import Attempt
from mario.snapshots.live_snapshots import ChunkSnapshot, followed_agent
from mario.snapshots.world_snapshot import AgentSnapshot, Area, MarioSnapshot, PowerState, WorldSnapshot
from mario.view.followed_agent_camera import FollowedAgentCamera
from tests.game.helpers import HOLD_LEFT, HOLD_NOTHING, HOLD_RIGHT, big_mario_attempt

GENERATION = 3
POPULATION_SIZE = 10
# A distinct x for every agent of the made-up chunks, so the rightmost is plain.
AGENT_SPACING_PIXELS = 16


def test_an_agent_snapshot_holds_position_facing_power_state_area_and_whether_he_is_still_in_his_attempt(flat_level):
    attempt = big_mario_attempt(flat_level)
    for _ in range(30):
        attempt.step(HOLD_RIGHT)
    attempt.step(HOLD_LEFT)
    agent = AgentSnapshot.of(7, attempt)
    assert agent.agent_index == 7
    assert agent.mario == MarioSnapshot.of(attempt.mario)
    assert agent.mario.power_state is PowerState.BIG
    assert not agent.faces_right
    assert agent.area is Area.LEVEL
    assert agent.is_in_attempt and not agent.reached_flag


def test_an_agent_whose_attempt_has_ended_is_no_longer_in_it(world_1_1: StaticLevel):
    attempt = Attempt(world_1_1, ends_on_stall=True)
    while not attempt.is_over:
        attempt.step(HOLD_NOTHING)
    agent = AgentSnapshot.of(0, attempt)
    assert not agent.is_in_attempt and not agent.reached_flag


def agent_at(agent_index: int, x_pixels: int, is_in_attempt: bool = True, reached_flag: bool = False) -> AgentSnapshot:
    return AgentSnapshot(agent_index, MarioSnapshot(x_pixels, 0, 12, 14), Area.LEVEL, is_in_attempt, reached_flag)


def test_the_followed_agent_is_the_rightmost_still_in_his_attempt():
    agents = [agent_at(0, 100), agent_at(1, 300, is_in_attempt=False), agent_at(2, 200)]
    assert followed_agent(agents, previously_followed_index=None).agent_index == 2


def test_on_a_tie_the_lowest_agent_index_is_followed():
    agents = [agent_at(4, 200), agent_at(2, 200), agent_at(3, 100)]
    assert followed_agent(agents, previously_followed_index=None).agent_index == 2


def test_once_every_attempt_has_ended_the_last_followed_agent_stays_followed():
    agents = [agent_at(0, 300, is_in_attempt=False), agent_at(1, 100, is_in_attempt=False)]
    assert followed_agent(agents, previously_followed_index=1).agent_index == 1
    assert followed_agent(agents, previously_followed_index=None).agent_index == 0


EMPTY_WORLD = WorldSnapshot.of(Attempt(StaticLevel(["." * 20] * 15)))


def world_of(agent: AgentSnapshot) -> WorldSnapshot:
    """A stand-in for the agent's whole world: only his Mario tells them apart."""
    return replace(EMPTY_WORLD, mario=agent.mario)


def chunk(agents: list[AgentSnapshot], generation: int = GENERATION,
          previously_followed_index: int | None = None) -> ChunkSnapshot:
    followed = followed_agent(agents, previously_followed_index)
    return ChunkSnapshot(generation, tuple(agents), followed.agent_index, world_of(followed))


def test_the_camera_shows_the_overall_rightmost_living_agents_world_with_the_others_as_ghosts():
    camera = FollowedAgentCamera()
    first_chunk = chunk([agent_at(0, 100), agent_at(1, 500), agent_at(2, 300)])
    second_chunk = chunk([agent_at(3, 400), agent_at(4, 200, is_in_attempt=False)])
    shown = camera.snapshot(GENERATION, POPULATION_SIZE, [first_chunk, second_chunk])
    assert shown.mario.x_pixels == 500
    # the others still in their attempt, the rightmost first; the ended one has vanished
    assert [ghost.agent_index for ghost in shown.ghosts] == [3, 2, 0]


def test_the_camera_cuts_to_the_next_rightmost_when_the_followed_agents_attempt_ends():
    camera = FollowedAgentCamera()
    camera.snapshot(GENERATION, POPULATION_SIZE, [chunk([agent_at(0, 100), agent_at(1, 500)])])
    shown = camera.snapshot(GENERATION, POPULATION_SIZE,
                            [chunk([agent_at(0, 110), agent_at(1, 500, is_in_attempt=False)])])
    assert shown.mario.x_pixels == 110
    assert shown.ghosts == ()


def test_once_everyone_has_ended_the_camera_stays_on_the_last_followed_agent():
    camera = FollowedAgentCamera()
    camera.snapshot(GENERATION, POPULATION_SIZE, [chunk([agent_at(0, 500)]), chunk([agent_at(1, 100)])])
    ended = [chunk([agent_at(0, 500, is_in_attempt=False)], previously_followed_index=0),
             chunk([agent_at(1, 100, is_in_attempt=False)], previously_followed_index=1)]
    assert camera.snapshot(GENERATION, POPULATION_SIZE, ended).mario.x_pixels == 500


def test_at_most_the_ghost_draw_limit_of_other_agents_are_ghosts_the_rightmost_ones():
    agents = [agent_at(agent, agent * AGENT_SPACING_PIXELS) for agent in range(GHOST_DRAW_LIMIT + 20)]
    shown = FollowedAgentCamera().snapshot(GENERATION, len(agents), [chunk(agents)])
    followed = len(agents) - 1
    assert [ghost.agent_index for ghost in shown.ghosts] == list(
        range(followed - 1, followed - 1 - GHOST_DRAW_LIMIT, -1))


def test_the_hud_line_counts_the_agents_still_in_their_attempt_and_those_that_reached_the_flag():
    """Agents of chunks not yet published haven't ended: they count as alive."""
    agents = [agent_at(0, 100), agent_at(1, 3000, is_in_attempt=False, reached_flag=True),
              agent_at(2, 200, is_in_attempt=False)]
    progress = FollowedAgentCamera().snapshot(GENERATION, POPULATION_SIZE, [chunk(agents)]).generation_progress
    assert (progress.generation, progress.alive, progress.population_size, progress.reached_flag) == (
        GENERATION, POPULATION_SIZE - 2, POPULATION_SIZE, 1)


def test_the_camera_ignores_chunks_still_showing_another_generation_and_slots_not_yet_written():
    camera = FollowedAgentCamera()
    assert camera.snapshot(GENERATION, POPULATION_SIZE, [None, chunk([agent_at(0, 100)], GENERATION - 1)]) is None
    shown = camera.snapshot(GENERATION, POPULATION_SIZE,
                            [chunk([agent_at(0, 100)], GENERATION - 1), chunk([agent_at(5, 50)])])
    assert shown.mario.x_pixels == 50 and shown.ghosts == ()


def test_the_camera_stays_on_a_chunks_last_followed_agent_when_the_one_it_followed_ended_unseen():
    """The window draws at its own pace and can miss ticks: here it last saw agent 0
    followed, but by the end his chunk had gone on to follow agent 1."""
    camera = FollowedAgentCamera()
    camera.snapshot(GENERATION, POPULATION_SIZE, [chunk([agent_at(0, 500), agent_at(1, 100)])])
    ended = chunk([agent_at(0, 500, is_in_attempt=False), agent_at(1, 120, is_in_attempt=False)],
                  previously_followed_index=1)
    assert camera.snapshot(GENERATION, POPULATION_SIZE, [ended]).mario.x_pixels == 120
