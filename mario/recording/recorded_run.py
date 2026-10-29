"""A run folder read back for replay and stats (spec sections 10, 11 and 13): its
recorded generations, its results.csv and generation_times.csv rows, and every
agent's Controller log.

It works on a run stopped early: a generation's folder is the last thing
recorded of it, so a generation counts as recorded once its folder holds its
Controller logs, whatever the run's config planned.
"""

import csv
from pathlib import Path

import numpy as np

from mario.constants.recording import CONTROLLER_LOG_KEY_FORMAT
from mario.recording.best_agent import best_agent_index
from mario.recording.generation_time_row import GenerationTimeRow
from mario.recording.results_row import ResultsRow
from mario.recording.run_folder import RunFolder


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
        self._check_is_recorded(generation)
        rows = sorted((row for row in self.results_rows() if row.generation == generation),
                      key=lambda row: row.agent_index)
        return rows[best_agent_index([row.fitness for row in rows])]

    def controller_log(self, generation: int, agent_index: int) -> np.ndarray:
        """The agent's Controller log: one uint8 bitmask per tick of its attempt."""
        with np.load(self._run_folder.controller_logs_path(generation)) as controller_logs:
            return controller_logs[CONTROLLER_LOG_KEY_FORMAT.format(agent=agent_index)]

    def controller_logs(self, generation: int) -> list[np.ndarray]:
        """Every agent's Controller log, in agent order. Raises LookupError if the generation isn't recorded."""
        self._check_is_recorded(generation)
        with np.load(self._run_folder.controller_logs_path(generation)) as controller_logs:
            return [controller_logs[CONTROLLER_LOG_KEY_FORMAT.format(agent=agent_index)]
                    for agent_index in range(len(controller_logs.files))]

    def _is_recorded(self, generation: int) -> bool:
        return self._run_folder.controller_logs_path(generation).is_file()

    def _check_is_recorded(self, generation: int) -> None:
        self._check_is_a_run_folder()
        if not self._is_recorded(generation):
            raise LookupError(f"generation {generation} isn't recorded in {self._run_folder.path}")

    def results_rows(self) -> list[ResultsRow]:
        """Every row of results.csv, in the order recorded. Raises LookupError if it isn't a run folder."""
        self._check_is_a_run_folder()
        with self._run_folder.results_path.open(newline="") as results_file:
            return [ResultsRow.parse(row) for row in csv.DictReader(results_file)]

    def generation_time_rows(self) -> list[GenerationTimeRow]:
        """Every row of generation_times.csv, in the order recorded. Raises LookupError if it isn't a run folder."""
        self._check_is_a_run_folder()
        with self._run_folder.generation_times_path.open(newline="") as generation_times_file:
            return [GenerationTimeRow.parse(row) for row in csv.DictReader(generation_times_file)]

    def _check_is_a_run_folder(self) -> None:
        if not self._run_folder.results_path.is_file():
            raise LookupError(f"{self._run_folder.path} is not a run folder: it has no results.csv")
