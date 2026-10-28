"""The followed-agent camera of a watched generation (spec section 8).

From the chunk snapshots the workers last published, it makes the one
WorldSnapshot the window draws: the overall followed agent's world, drawn solid,
with up to GHOST_DRAW_LIMIT other living agents (the rightmost ones) as ghosts
and the generation's line for the HUD. An agent vanishes once his attempt ends;
when the followed agent's ends, the camera cuts to the new rightmost living one,
and once every attempt has ended it stays on the last one followed.
"""

from collections.abc import Sequence
from dataclasses import replace

from mario.constants.view import GHOST_DRAW_LIMIT
from mario.snapshots.live_snapshots import ChunkSnapshot, followed_agent, rightmost_first
from mario.snapshots.world_snapshot import GenerationProgress, WorldSnapshot


class FollowedAgentCamera:
    def __init__(self):
        self._followed_agent: int | None = None

    def snapshot(self, generation: int, population_size: int,
                 chunk_snapshots: Sequence[ChunkSnapshot | None]) -> WorldSnapshot | None:
        """What to draw of the generation, or None until a chunk of it has been published.

        Slots not yet written (None) and chunks still showing an earlier
        generation are left out; agents of chunks not yet published count as alive."""
        chunks = [chunk for chunk in chunk_snapshots if chunk is not None and chunk.generation == generation]
        if not chunks:
            return None
        agents = [agent for chunk in chunks for agent in chunk.agents]
        # Each chunk's own followed agent: only their worlds were published, and the
        # overall followed agent is always one of them.
        followed_per_chunk = {chunk.followed_agent for chunk in chunks}
        candidates = [agent for agent in agents if agent.agent in followed_per_chunk]
        if self._followed_agent not in followed_per_chunk:  # another generation's, or no longer his chunk's
            self._followed_agent = None
        followed = followed_agent(candidates, self._followed_agent)
        self._followed_agent = followed.agent
        followed_world = next(chunk.followed_world for chunk in chunks if chunk.followed_agent == followed.agent)
        ghosts = rightmost_first([agent for agent in agents if agent.is_in_attempt and agent.agent != followed.agent])
        ended_count = sum(not agent.is_in_attempt for agent in agents)
        reached_flag_count = sum(agent.reached_flag for agent in agents)
        return replace(followed_world, ghosts=tuple(ghosts[:GHOST_DRAW_LIMIT]),
                       generation_progress=GenerationProgress(generation, population_size - ended_count,
                                                              population_size, reached_flag_count))
