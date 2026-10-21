"""Two simulation shapes for playing one generation, plus a process-pool wrapper. PROTOTYPE.

Shape A, PerAgentRunner: each agent plays its whole attempt on its own, asking
its own brain one observation at a time.

Shape B, LockstepBatchedRunner: all agents of a chunk advance one tick together;
observations are gathered in one numpy call and every brain is evaluated in one
stacked matmul. Physics stays per-agent OOP.

Both record each agent's Controller buttons per tick (one byte per tick).
With use_scripted_pilot the brain still runs (same cost) but ScriptedPilot
presses the buttons, to time long, late-generation attempts.
"""

import multiprocessing
from dataclasses import dataclass

import numpy as np

from . import constants as c
from .attempt import Attempt
from .level import StaticLevel
from .observation import TileGridObserver
from .placeholder_brain import PlaceholderBrain, PlaceholderBrainBatch
from .scripted_pilot import ScriptedPilot

BATCH_COMPACTION_FRACTION = 0.5     # shrink the brain batch once half its rows have finished


@dataclass(slots=True)
class AttemptResult:
    controller_log: bytes           # one Controller bitmask per tick
    end: str
    ticks: int
    best_x_pixels: int
    final_state_digest: str


def _result_of(attempt: Attempt, controller_log: bytearray) -> AttemptResult:
    return AttemptResult(bytes(controller_log), attempt.end.value, attempt.tick,
                         attempt.best_x // c.SUBPIXELS_PER_PIXEL, attempt.state_digest())


class PerAgentRunner:
    name = "per-agent objects"

    def __init__(self, level: StaticLevel, decision_interval_ticks: int,
                 use_scripted_pilot: bool = False):
        self.level = level
        self.observer = TileGridObserver(level)
        self.decision_interval_ticks = decision_interval_ticks
        self.pilot = (ScriptedPilot(level, c.SCRIPTED_PILOT_LOOK_AHEAD_TILES)
                      if use_scripted_pilot else None)

    def run_generation(self, parameters: np.ndarray) -> list[AttemptResult]:
        return [self.run_attempt(agent_parameters) for agent_parameters in parameters]

    def run_attempt(self, agent_parameters: np.ndarray) -> AttemptResult:
        attempt = Attempt(self.level)
        brain = PlaceholderBrain(agent_parameters)
        observation = np.empty(c.OBSERVATION_SIZE)
        controller_log = bytearray()
        buttons = 0
        interval = self.decision_interval_ticks
        while attempt.end is None:
            if attempt.tick % interval == 0:
                self.observer.observe(attempt, observation)
                buttons = brain.choose_buttons(observation)
            if self.pilot:
                buttons = self.pilot.choose_buttons(attempt)
            controller_log.append(buttons)
            attempt.step(buttons)
        return _result_of(attempt, controller_log)


class LockstepBatchedRunner:
    name = "lock-step, batched brain"

    def __init__(self, level: StaticLevel, decision_interval_ticks: int,
                 use_scripted_pilot: bool = False):
        self.level = level
        self.observer = TileGridObserver(level)
        self.decision_interval_ticks = decision_interval_ticks
        self.pilot = (ScriptedPilot(level, c.SCRIPTED_PILOT_LOOK_AHEAD_TILES)
                      if use_scripted_pilot else None)

    def run_generation(self, parameters: np.ndarray) -> list[AttemptResult]:
        agent_count = len(parameters)
        attempts = [Attempt(self.level) for _ in range(agent_count)]
        controller_logs = [bytearray() for _ in range(agent_count)]
        buttons = [0] * agent_count
        brain = PlaceholderBrainBatch(parameters)
        row_of_agent = {agent: agent for agent in range(agent_count)}   # brain row holding each agent
        observations = np.zeros((agent_count, c.OBSERVATION_SIZE))
        active_agents = list(range(agent_count))
        tick = 0
        while active_agents:
            if tick % self.decision_interval_ticks == 0:
                if len(active_agents) < brain.row_count * BATCH_COMPACTION_FRACTION:
                    row_of_agent, observations = self._compact(brain, row_of_agent, active_agents)
                active_rows = [row_of_agent[agent] for agent in active_agents]
                self.observer.observe_many([attempts[agent] for agent in active_agents],
                                           observations, np.array(active_rows, dtype=np.intp))
                chosen_by_row = brain.choose_buttons(observations).tolist()
                for agent, row in zip(active_agents, active_rows):
                    buttons[agent] = chosen_by_row[row]
            if self.pilot:
                for agent in active_agents:
                    buttons[agent] = self.pilot.choose_buttons(attempts[agent])
            still_active = []
            for agent in active_agents:
                attempt = attempts[agent]
                agent_buttons = buttons[agent]
                controller_logs[agent].append(agent_buttons)
                attempt.step(agent_buttons)
                if attempt.end is None:
                    still_active.append(agent)
            active_agents = still_active
            tick += 1
        return [_result_of(attempt, log) for attempt, log in zip(attempts, controller_logs)]

    @staticmethod
    def _compact(brain, row_of_agent, active_agents):
        brain.keep_rows(np.array([row_of_agent[agent] for agent in active_agents], dtype=np.intp))
        new_row_of_agent = {agent: row for row, agent in enumerate(active_agents)}
        return new_row_of_agent, np.zeros((len(active_agents), c.OBSERVATION_SIZE))


RUNNER_SHAPES = {runner.name: runner for runner in (PerAgentRunner, LockstepBatchedRunner)}

# --- process pool ---------------------------------------------------------------

_worker_level: StaticLevel | None = None


def _initialise_worker() -> None:
    global _worker_level
    _worker_level = StaticLevel.load_world_1_1()        # each process loads the shared level once


def _run_chunk(task: tuple[str, int, bool, np.ndarray]) -> list[AttemptResult]:
    shape_name, decision_interval_ticks, use_scripted_pilot, parameters = task
    runner = RUNNER_SHAPES[shape_name](_worker_level, decision_interval_ticks, use_scripted_pilot)
    return runner.run_generation(parameters)


class ParallelGenerationRunner:
    """Splits the population into chunks and plays them on a persistent process pool."""

    def __init__(self, shape_name: str, decision_interval_ticks: int, use_scripted_pilot: bool,
                 pool, worker_count: int):
        self.shape_name = shape_name
        self.decision_interval_ticks = decision_interval_ticks
        self.use_scripted_pilot = use_scripted_pilot
        self.pool = pool
        self.worker_count = worker_count
        self.name = f"{shape_name}, {worker_count} processes"

    @staticmethod
    def create_pool(worker_count: int):
        return multiprocessing.get_context("spawn").Pool(worker_count, initializer=_initialise_worker)

    def run_generation(self, parameters: np.ndarray) -> list[AttemptResult]:
        chunk_count = self.worker_count * c.CHUNKS_PER_WORKER
        tasks = [(self.shape_name, self.decision_interval_ticks, self.use_scripted_pilot, chunk)
                 for chunk in np.array_split(parameters, chunk_count)]
        results: list[AttemptResult] = []
        for chunk_results in self.pool.map(_run_chunk, tasks, chunksize=1):
            results.extend(chunk_results)
        return results
