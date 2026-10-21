"""Issue #4 benchmark: can 100 generations x 1000 agents finish in ~2 hours? PROTOTYPE.

Run from the repo root:   py -m prototype.simulation_speed.benchmark
Prints markdown tables (copied into prototype/simulation-speed.md).
"""

import os

# one BLAS thread per process: 8 worker processes must not each spawn 8 BLAS threads
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import platform
import statistics
import sys
import time

import numpy as np

from . import constants as c
from .attempt import Attempt
from .determinism import ReplayVerifier, replay_attempt
from .generation_runners import (LockstepBatchedRunner, ParallelGenerationRunner,
                                 PerAgentRunner)
from .level import StaticLevel
from .placeholder_brain import random_placeholder_parameters
from .scripted_pilot import ScriptedPilot

SECONDS_PER_MINUTE = 60
WORKLOADS = {"random brains": False, "scripted pilot (long attempts)": True}


class GenerationTiming:
    """Wall time and tick totals of one runner configuration over a few generations."""

    def __init__(self, label: str, seconds: list[float], results_per_generation: list[list]):
        self.label = label
        self.seconds_per_generation = statistics.median(seconds)
        all_results = [result for results in results_per_generation for result in results]
        self.mean_ticks_per_attempt = statistics.fmean(result.ticks for result in all_results)
        self.agent_ticks_per_second = sum(result.ticks for result in all_results) / sum(seconds)
        self.first_results = results_per_generation[0]   # seed BENCHMARK_SEED in every configuration

    def projected_run_minutes(self, ticks_per_attempt: float | None = None) -> float:
        if ticks_per_attempt is None:
            seconds = self.seconds_per_generation
        else:
            seconds = c.POPULATION_SIZE * ticks_per_attempt / self.agent_ticks_per_second
        return seconds * c.GENERATIONS_IN_RUN / SECONDS_PER_MINUTE


def time_generations(label: str, runner, generation_count: int, first_seed: int) -> GenerationTiming:
    seconds, results_per_generation = [], []
    for generation in range(generation_count):
        parameters = random_placeholder_parameters(
            c.POPULATION_SIZE, np.random.default_rng(first_seed + generation))
        start = time.perf_counter()
        results = runner.run_generation(parameters)
        seconds.append(time.perf_counter() - start)
        results_per_generation.append(results)
    timing = GenerationTiming(label, seconds, results_per_generation)
    print(f"  timed: {label}: {timing.seconds_per_generation:.2f} s/generation", flush=True)
    return timing


def measure_single_agent(level) -> list[tuple[str, float]]:
    """Ticks per second for one agent, peeling the cost apart layer by layer."""
    pilot = ScriptedPilot(level, c.SCRIPTED_PILOT_LOOK_AHEAD_TILES)
    recorded_attempt, controller_log = Attempt(level), bytearray()
    while not recorded_attempt.is_over:
        buttons = pilot.choose_buttons(recorded_attempt)
        controller_log.append(buttons)
        recorded_attempt.step(buttons)
    repeats = max(1, c.SINGLE_AGENT_BENCHMARK_TICKS // len(controller_log))
    total_ticks = repeats * len(controller_log)

    start = time.perf_counter()
    for _ in range(repeats):
        replay_attempt(level, bytes(controller_log))
    physics_rate = total_ticks / (time.perf_counter() - start)

    parameters = random_placeholder_parameters(1, np.random.default_rng(c.BENCHMARK_SEED))[0]
    runner = PerAgentRunner(level, decision_interval_ticks=1, use_scripted_pilot=True)
    start = time.perf_counter()
    for _ in range(repeats):
        runner.run_attempt(parameters)
    full_rate = total_ticks / (time.perf_counter() - start)
    return [("physics only (replaying a recorded Controller log)", physics_rate),
            ("physics + observation + placeholder brain + pilot, every tick", full_rate)]


def print_generation_table(timings: list[GenerationTiming]) -> None:
    print("\n| Workload / shape | s per generation | mean ticks per attempt | agent-ticks/s "
          "| 100 generations, measured | 100 generations at 2400 ticks/attempt "
          "| 100 generations at 9600 ticks/attempt (timer) |")
    print("|---|---|---|---|---|---|---|")
    for timing in timings:
        print(f"| {timing.label} | {timing.seconds_per_generation:.2f} "
              f"| {timing.mean_ticks_per_attempt:.0f} | {timing.agent_ticks_per_second:,.0f} "
              f"| {timing.projected_run_minutes():.1f} min "
              f"| {timing.projected_run_minutes(c.PESSIMISTIC_TICKS_PER_ATTEMPT):.1f} min "
              f"| {timing.projected_run_minutes(c.LEVEL_TIMER_TICKS):.1f} min |")


def main() -> None:
    print(f"cpu_count={os.cpu_count()} python={sys.version.split()[0]} numpy={np.__version__} "
          f"platform={platform.platform()} processor={platform.processor()}")
    level = StaticLevel.load_world_1_1()

    print("\n## Single agent")
    print("\n| What is stepped | ticks/s |\n|---|---|")
    for label, rate in measure_single_agent(level):
        print(f"| {label} | {rate:,.0f} |")

    shapes = (PerAgentRunner, LockstepBatchedRunner)
    timings: list[GenerationTiming] = []
    single_process_results = {}
    print("\n## Generation timings (decision every tick)")
    for workload, use_pilot in WORKLOADS.items():
        for shape in shapes:
            runner = shape(level, decision_interval_ticks=1, use_scripted_pilot=use_pilot)
            timing = time_generations(f"{workload} / {shape.name}, 1 process", runner,
                                      c.TIMED_GENERATIONS_SINGLE_PROCESS, c.BENCHMARK_SEED)
            timings.append(timing)
            single_process_results[(workload, shape.name)] = timing.first_results

    pool_start = time.perf_counter()
    pool = ParallelGenerationRunner.create_pool(c.WORKER_PROCESSES)
    pool.map(abs, range(c.WORKER_PROCESSES))               # force every worker to start
    pool_startup_seconds = time.perf_counter() - pool_start
    parallel_results = {}
    with pool:
        for interval in c.DECISION_INTERVALS_TICKS:
            for workload, use_pilot in WORKLOADS.items():
                for shape in shapes:
                    runner = ParallelGenerationRunner(shape.name, interval, use_pilot, pool,
                                                      c.WORKER_PROCESSES)
                    label = f"{workload} / {runner.name}, decision every {interval} tick(s)"
                    timing = time_generations(label, runner, c.TIMED_GENERATIONS_PARALLEL,
                                              c.BENCHMARK_SEED)
                    timings.append(timing)
                    parallel_results[(workload, shape.name, interval)] = timing.first_results
        repeat_runner = ParallelGenerationRunner(LockstepBatchedRunner.name, 1, False, pool,
                                                 c.WORKER_PROCESSES)
        repeat_results = repeat_runner.run_generation(random_placeholder_parameters(
            c.POPULATION_SIZE, np.random.default_rng(c.BENCHMARK_SEED)))

    for worker_count in c.ALTERNATIVE_WORKER_COUNTS:
        with ParallelGenerationRunner.create_pool(worker_count) as smaller_pool:
            runner = ParallelGenerationRunner(LockstepBatchedRunner.name, 1, True, smaller_pool,
                                              worker_count)
            timings.append(time_generations(
                f"scripted pilot (long attempts) / {runner.name}, decision every 1 tick(s)",
                runner, c.TIMED_GENERATIONS_PARALLEL, c.BENCHMARK_SEED))

    print_generation_table(timings)
    print(f"\nProcess pool start-up ({c.WORKER_PROCESSES} spawned workers): "
          f"{pool_startup_seconds:.2f} s, paid once per run.")

    print("\n## Determinism")
    verifier = ReplayVerifier(level)
    random_workload = "random brains"
    checks = []
    for shape in shapes:
        results = single_process_results[(random_workload, shape.name)]
        checks.append((f"replay in-process, {shape.name} (1 process)",
                       verifier.count_replay_mismatches(results), len(results)))
    for (workload, shape_name, interval), results in parallel_results.items():
        if interval == 1:
            checks.append((f"replay in parent of attempts simulated in workers, {workload} / {shape_name}",
                           verifier.count_replay_mismatches(results), len(results)))
    lockstep_parallel = parallel_results[(random_workload, LockstepBatchedRunner.name, 1)]
    checks.append(("same genomes, lock-step parallel run twice (differing agents)",
                   verifier.count_differing_attempts(lockstep_parallel, repeat_results),
                   len(repeat_results)))
    for shape in shapes:
        checks.append((f"same genomes, {shape.name}: 1 process vs {c.WORKER_PROCESSES} processes "
                       "(differing agents)",
                       verifier.count_differing_attempts(
                           single_process_results[(random_workload, shape.name)],
                           parallel_results[(random_workload, shape.name, 1)]),
                       c.POPULATION_SIZE))
    checks.append(("same genomes, per-agent brain vs batched brain (differing agents)",
                   verifier.count_differing_attempts(
                       single_process_results[(random_workload, PerAgentRunner.name)],
                       single_process_results[(random_workload, LockstepBatchedRunner.name)]),
                   c.POPULATION_SIZE))
    print("\n| Check | mismatches | attempts |\n|---|---|---|")
    for label, mismatches, attempts in checks:
        print(f"| {label} | {mismatches} | {attempts} |")


if __name__ == "__main__":
    main()
