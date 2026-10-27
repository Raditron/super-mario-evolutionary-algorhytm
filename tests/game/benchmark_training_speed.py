"""Seconds per generation of 1000 agents on the full game (#26's speed criterion).

Not a test, so pytest doesn't collect it. From the repo root, run:

    py -m tests.game.benchmark_training_speed

It times the real Trainer on the real AgentWorkerPool, as `py -m mario train`
runs them, with two workloads (as in docs/research/simulation-speed.md):

- random: the random-buttons test double. Honest early generations: short
  attempts, mostly stalls.
- long: every agent walks the whole level. Its brain pays for a placeholder
  network every tick (OBSERVATION_LENGTH = 160 inputs -> 24 tanh -> 5, random
  weights that never learn, one stacked matmul for the chunk) but throws the
  answer away and presses a scripted pilot's recorded buttons instead. The
  placeholder is a timing tool only, not the user's network, and nothing here
  is a GA.

For each it prints the median seconds per generation and the projection for
100 generations, both as measured and with every attempt lasting 2400 ticks.
"""

import os
import platform
import statistics
import sys

import numpy as np

from mario.constants.controller import CONTROLLER_BUTTONS
from mario.constants.observation import OBSERVATION_LENGTH
from mario.constants.training import TRAINING_WORKER_COUNT
from mario.controller.controller_bitmask import held_buttons_from_bitmasks
from mario.level.static_level import StaticLevel
from mario.simulation.attempt import Attempt
from mario.simulation.attempt_result import AttemptResult
from mario.training.agent_worker_pool import AgentWorkerPool
from mario.training.algorithm_factory import AlgorithmFactory
from mario.training.neuroevolution_algorithm import Brain, NeuroevolutionAlgorithm
from mario.training.run_config import RunSettings
from mario.training.trainer import GenerationListener, GenerationReport, Trainer
from tests.game.random_buttons_algorithm import create_random_buttons_algorithm
from tests.game.scripted_pilot import ScriptedPilot

BENCHMARK_POPULATION_SIZE = 1000
TIMED_GENERATIONS = 3
BENCHMARK_SEED = 4
# The projections: this many generations, and attempts of this many ticks.
PROJECTED_GENERATIONS = 100
PROJECTED_TICKS_PER_ATTEMPT = 2400
# The speed bar of spec section 9.
BUDGET_MINUTES = 120
SECONDS_PER_MINUTE = 60

# The placeholder network's hidden layer (the size #4 timed).
PLACEHOLDER_HIDDEN_UNITS = 24
PLACEHOLDER_WEIGHT_COUNT = OBSERVATION_LENGTH * PLACEHOLDER_HIDDEN_UNITS + PLACEHOLDER_HIDDEN_UNITS * len(
    CONTROLLER_BUTTONS)
# The pilot also jumps at an undefeated enemy whose left edge is at most this far
# ahead of Mario's; at this distance it walks all of 1-1 to the castle.
ENEMY_LOOK_AHEAD_PIXELS = 32
PILOT_LOG_SETTING = "pilot_controller_log"


def pilot_controller_log() -> list[int]:
    """The pilot's buttons, tick by tick, for one training attempt through World 1-1."""
    attempt = Attempt(StaticLevel.load_world_1_1(), ends_on_stall=True)
    pilot = ScriptedPilot(enemy_look_ahead_pixels=ENEMY_LOOK_AHEAD_PIXELS)
    buttons_per_tick = []
    while not attempt.is_over:
        buttons_per_tick.append(pilot.next_buttons(attempt))
        attempt.step(buttons_per_tick[-1])
    return buttons_per_tick


class PilotReplayBrain:
    def __init__(self, genomes: list[np.ndarray], pilot_decisions: np.ndarray):
        weights = np.stack(genomes)
        hidden_weight_count = OBSERVATION_LENGTH * PLACEHOLDER_HIDDEN_UNITS
        self._hidden_weights = weights[:, :hidden_weight_count].reshape(
            len(genomes), OBSERVATION_LENGTH, PLACEHOLDER_HIDDEN_UNITS)
        self._output_weights = weights[:, hidden_weight_count:].reshape(
            len(genomes), PLACEHOLDER_HIDDEN_UNITS, len(CONTROLLER_BUTTONS))
        self._pilot_decisions = pilot_decisions
        self._ticks_decided = 0

    def decide(self, observations: np.ndarray) -> np.ndarray:
        hidden = np.tanh(observations[:, None, :] @ self._hidden_weights)
        _thrown_away = (hidden @ self._output_weights)[:, 0, :] > 0
        tick = min(self._ticks_decided, len(self._pilot_decisions) - 1)
        self._ticks_decided += 1
        return np.repeat(self._pilot_decisions[tick][None, :], len(observations), axis=0)


class PilotReplayAlgorithm(NeuroevolutionAlgorithm):
    def __init__(self, pilot_log: list[int]):
        self._pilot_decisions = held_buttons_from_bitmasks(np.array(pilot_log, dtype=np.uint8))

    def initial_genomes(self, population_size: int, rng: np.random.Generator) -> list[np.ndarray]:
        return [rng.standard_normal(PLACEHOLDER_WEIGHT_COUNT) for _ in range(population_size)]

    def build_brain(self, genomes: list[np.ndarray]) -> Brain:
        return PilotReplayBrain(genomes, self._pilot_decisions)

    def fitness(self, attempt_result: AttemptResult) -> float:
        return float(attempt_result.furthest_x)

    def next_genomes(self, genomes: list[np.ndarray], fitnesses: np.ndarray,
                     rng: np.random.Generator) -> list[np.ndarray]:
        return genomes


def create_pilot_replay_algorithm(settings: dict) -> PilotReplayAlgorithm:
    return PilotReplayAlgorithm(settings[PILOT_LOG_SETTING])


class GenerationTimer(GenerationListener):
    def __init__(self):
        self.seconds: list[float] = []
        self.agent_ticks: list[int] = []

    def generation_finished(self, report: GenerationReport) -> None:
        self.seconds.append(report.seconds)
        self.agent_ticks.append(sum(played.attempt_result.ticks_elapsed for played in report.played_attempts))


def time_workload(name: str, algorithm_factory: AlgorithmFactory) -> None:
    timer = GenerationTimer()
    run_settings = RunSettings(name=name, seed=BENCHMARK_SEED, generations=TIMED_GENERATIONS,
                               population_size=BENCHMARK_POPULATION_SIZE)
    with AgentWorkerPool(algorithm_factory) as worker_pool:
        Trainer(algorithm_factory.create(), worker_pool, run_settings, timer).run()
    seconds_per_generation = statistics.median(timer.seconds)
    agent_ticks_per_second = sum(timer.agent_ticks) / sum(timer.seconds)
    ticks_per_attempt = sum(timer.agent_ticks) / (TIMED_GENERATIONS * BENCHMARK_POPULATION_SIZE)
    measured_minutes = PROJECTED_GENERATIONS * seconds_per_generation / SECONDS_PER_MINUTE
    projected_minutes = (PROJECTED_GENERATIONS * BENCHMARK_POPULATION_SIZE * PROJECTED_TICKS_PER_ATTEMPT
                         / agent_ticks_per_second / SECONDS_PER_MINUTE)
    print(f"| {name} | {seconds_per_generation:.2f} | {', '.join(f'{s:.2f}' for s in timer.seconds)} "
          f"| {ticks_per_attempt:.0f} | {agent_ticks_per_second:,.0f} | {measured_minutes:.1f} min "
          f"| {projected_minutes:.1f} min{' **over budget**' if projected_minutes > BUDGET_MINUTES else ''} |",
          flush=True)


def main() -> None:
    print(f"Machine: {platform.processor()}, os.cpu_count() = {os.cpu_count()}; {platform.platform()}; "
          f"Python {platform.python_version()}, numpy {np.__version__}; {TRAINING_WORKER_COUNT} workers; "
          f"{BENCHMARK_POPULATION_SIZE} agents; median of {TIMED_GENERATIONS} generations\n")
    print(f"| workload | s/gen (median) | each generation, s | ticks/attempt | agent-ticks/s "
          f"| {PROJECTED_GENERATIONS} gen, measured | {PROJECTED_GENERATIONS} gen at "
          f"{PROJECTED_TICKS_PER_ATTEMPT} ticks |")
    print("|---|---|---|---|---|---|---|")
    time_workload("random buttons (test double)", AlgorithmFactory(create_random_buttons_algorithm, {}))
    time_workload("long attempts (pilot + placeholder network)", AlgorithmFactory(
        create_pilot_replay_algorithm, {PILOT_LOG_SETTING: pilot_controller_log()}))


if __name__ == "__main__":
    sys.exit(main())
