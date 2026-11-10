"""The numbers the presentation quotes, read from one recorded training run: its settings, every
generation's best and average fitness, and the moments worth naming."""

import csv
import tomllib
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from presentation_constants import FLAG_END_REASON, SECONDS_PER_HOUR, TICKS_PER_SECOND

RESULTS_FILE = "results.csv"
CONFIG_FILE = "config.toml"
GENERATIONS_FOLDER = "generations"
BEST_GENOME_FILE = "best_genome.npy"
GENERATION_TIMES_FILE = "generation_times.csv"


@dataclass(frozen=True)
class RunFacts:
    settings: dict  # config.toml's [run] and [algorithm] tables, merged
    generations: list[int]
    best_fitness: list[float]  # per generation, in the order of generations
    average_fitness: list[float]
    finishers: list[int]
    first_flag_generation: int
    best_fitness_without_flag: float
    best_fitness_overall: float
    fastest_finish_seconds: float
    last_best_genome: np.ndarray
    total_hours: float

    @property
    def last_generation(self) -> int:
        return self.generations[-1]

    @property
    def last_finishers(self) -> int:
        return self.finishers[-1]

    @property
    def genome_size(self) -> int:
        return self.last_best_genome.size


def read_run_facts(run_folder: Path) -> RunFacts:
    with open(run_folder / CONFIG_FILE, "rb") as config_file:
        config = tomllib.load(config_file)
    settings = {**config["run"], **config["algorithm"]}

    attempts_by_generation: dict[int, list[dict]] = defaultdict(list)
    with open(run_folder / RESULTS_FILE, newline="") as results_file:
        for attempt in csv.DictReader(results_file):
            attempts_by_generation[int(attempt["generation"])].append(attempt)

    generations = sorted(attempts_by_generation)
    best_fitness, average_fitness, finishers = [], [], []
    for generation in generations:
        fitnesses = [float(attempt["fitness"]) for attempt in attempts_by_generation[generation]]
        best_fitness.append(max(fitnesses))
        average_fitness.append(sum(fitnesses) / len(fitnesses))
        finishers.append(sum(1 for attempt in attempts_by_generation[generation] if _finished(attempt)))

    every_attempt = [attempt for attempts in attempts_by_generation.values() for attempt in attempts]
    finished_attempts = [attempt for attempt in every_attempt if _finished(attempt)]
    with open(run_folder / GENERATION_TIMES_FILE, newline="") as times_file:
        total_seconds = sum(float(row["seconds"]) for row in csv.DictReader(times_file))
    last_generation_folder = sorted((run_folder / GENERATIONS_FOLDER).iterdir())[-1]

    return RunFacts(
        settings=settings,
        generations=generations,
        best_fitness=best_fitness,
        average_fitness=average_fitness,
        finishers=finishers,
        first_flag_generation=next(
            generation for generation, count in zip(generations, finishers) if count > 0),
        best_fitness_without_flag=max(
            float(attempt["fitness"]) for attempt in every_attempt if not _finished(attempt)),
        best_fitness_overall=max(best_fitness),
        fastest_finish_seconds=min(
            int(attempt["ticks_elapsed"]) for attempt in finished_attempts) / TICKS_PER_SECOND,
        last_best_genome=np.load(last_generation_folder / BEST_GENOME_FILE),
        total_hours=total_seconds / SECONDS_PER_HOUR,
    )


def _finished(attempt: dict) -> bool:
    return attempt["end_reason"] == FLAG_END_REASON
