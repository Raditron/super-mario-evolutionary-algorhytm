"""A run folder read back for replay (spec sections 10 and 11): its recorded
generations, each one's results.csv rows, and every agent's Controller log.

It works on a run stopped early: a generation's folder is the last thing
recorded of it, so a generation counts as recorded once its folder holds its
Controller logs, whatever the run's config planned.
"""

import csv
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from mario.constants.recording import CONTROLLER_LOG_KEY_FORMAT
from mario.recording.run_folder import RunFolder
from mario.simulation.attempt_result import EndReason


@dataclass(frozen=True)
class ResultsRow:
    """One agent's row of results.csv: its fitness and its attempt's end-of-attempt facts."""
    generation: int
    agent: int
    fitness: float
    end_reason: EndReason
    furthest_x: int
    ticks_elapsed: int
    final_score: int
    coins_collected: int

    @classmethod
    def parse(cls, row: dict[str, str]) -> "ResultsRow":
        """A row as csv.DictReader reads it, keyed by the RESULTS_COLUMNS."""
        return cls(int(row["generation"]), int(row["agent"]), float(row["fitness"]), EndReason(row["end_reason"]),
                   int(row["furthest_x"]), int(row["ticks_elapsed"]), int(row["final_score"]),
                   int(row["coins_collected"]))


class RecordedRun:
    def __init__(self, run_folder_path: Path):
        self._run_folder = RunFolder(run_folder_path)

    def last_generation(self) -> int:
        """The highest-numbered generation recorded. Raises LookupError if there is none yet."""
        self._check_is_a_run_folder()
        recorded_generations = [int(folder.name) for folder in self._run_folder.generations_path.glob("*")
                                if folder.name.isdigit() and self._is_recorded(int(folder.name))]
        if not recorded_generations:
            raise LookupError(f"{self._run_folder.path} has no generation recorded yet")
        return max(recorded_generations)

    def best_agent(self, generation: int) -> ResultsRow:
        """The generation's row with the highest fitness; on a tie, the lowest agent index.
        Raises LookupError if the generation isn't recorded."""
        self._check_is_a_run_folder()
        if not self._is_recorded(generation):
            raise LookupError(f"generation {generation} isn't recorded in {self._run_folder.path}")
        rows = [row for row in self._results_rows() if row.generation == generation]
        return max(rows, key=lambda row: (row.fitness, -row.agent))

    def controller_log(self, generation: int, agent: int) -> np.ndarray:
        """The agent's Controller log: one uint8 bitmask per tick of its attempt."""
        with np.load(self._run_folder.controller_logs_path(generation)) as controller_logs:
            return controller_logs[CONTROLLER_LOG_KEY_FORMAT.format(agent=agent)]

    def _is_recorded(self, generation: int) -> bool:
        return self._run_folder.controller_logs_path(generation).is_file()

    def _results_rows(self) -> list[ResultsRow]:
        with self._run_folder.results_path.open(newline="") as results_file:
            return [ResultsRow.parse(row) for row in csv.DictReader(results_file)]

    def _check_is_a_run_folder(self) -> None:
        if not self._run_folder.results_path.is_file():
            raise LookupError(f"{self._run_folder.path} is not a run folder: it has no results.csv")
