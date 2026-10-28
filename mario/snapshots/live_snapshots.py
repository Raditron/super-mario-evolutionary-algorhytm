"""What one worker publishes of its chunk every tick while a generation is watched (spec section 11).

Every agent of the chunk, in brief, plus the whole world of the chunk's own
followed agent. The window follows the overall rightmost living agent, and by
the followed-agent rule he is always his own chunk's followed agent, so his
world is in his chunk's snapshot.
"""

from collections.abc import Sequence
from dataclasses import dataclass

from mario.snapshots.world_snapshot import AgentSnapshot, WorldSnapshot


@dataclass(frozen=True)
class ChunkSnapshot:
    generation: int
    agents: tuple[AgentSnapshot, ...]
    followed_agent_index: int                         # his index within the generation
    followed_world: WorldSnapshot                     # with his Observation, for the Debug view


def followed_agent(agents: Sequence[AgentSnapshot], previously_followed_index: int | None) -> AgentSnapshot:
    """The followed agent: the rightmost still in his attempt, the lowest index on a
    tie. Once every attempt has ended, the one followed before stays followed (with
    none before, the rightmost of all)."""
    living_agents = [agent for agent in agents if agent.is_in_attempt]
    if not living_agents and previously_followed_index is not None:
        return next(agent for agent in agents if agent.agent_index == previously_followed_index)
    return max(living_agents or agents, key=_rank)


def rightmost_first(agents: Sequence[AgentSnapshot]) -> list[AgentSnapshot]:
    """The agents ordered as the followed-agent rule ranks them, the rightmost first."""
    return sorted(agents, key=_rank, reverse=True)


def _rank(agent: AgentSnapshot) -> tuple[int, int]:
    return agent.ranking_x_pixels, -agent.agent_index
