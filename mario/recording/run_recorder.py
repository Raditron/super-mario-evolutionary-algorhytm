"""Writes a run's folder (spec section 10): made when the run starts, added to once per finished generation.

Nothing of a generation is written until it has finished, and Ctrl+C waits
while one is being written, so a stopped run leaves only complete generations.
"""

import csv
import shutil
import signal
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

import numpy as np

from mario.constants.recording import CONTROLLER_LOG_KEY_FORMAT, GENERATION_TIMES_COLUMNS, RESULTS_COLUMNS
from mario.recording.best_agent import best_agent_index
from mario.recording.generation_time_row import GenerationTimeRow
from mario.recording.results_row import ResultsRow
from mario.recording.run_folder import RunFolder
from mario.simulation.attempt_result import AttemptResult


class RunRecorder:
    def __init__(self, run_folder: RunFolder):
        """Records into a run folder that start has made."""
        self._run_folder = run_folder

    @classmethod
    def start(cls, runs_root: Path, run_name: str, config_path: Path, started_at: datetime) -> "RunRecorder":
        """Make the run's folder, with a copy of its config and the CSVs' header rows.

        Raises FileExistsError if a run of this name started in the same minute."""
        run_folder = RunFolder.for_new_run(runs_root, run_name, started_at)
        run_folder.path.mkdir(parents=True)
        shutil.copyfile(config_path, run_folder.config_copy_path)
        _append_rows(run_folder.results_path, [RESULTS_COLUMNS])
        _append_rows(run_folder.generation_times_path, [GENERATION_TIMES_COLUMNS])
        return cls(run_folder)

    @property
    def run_folder_path(self) -> Path:
        return self._run_folder.path

    def record_generation(self, generation: int, attempt_results: list[AttemptResult],
                          controller_logs: list[np.ndarray], fitnesses: np.ndarray,
                          genomes: list[np.ndarray], seconds: float) -> None:
        """Record one finished generation; every list lines up by agent index.

        In this order: its rows of results.csv, its row of generation_times.csv,
        then its generation folder, with every Controller log and the best genome.
        Ctrl+C pressed meanwhile stops the run once the generation is complete."""
        with _ctrl_c_held_back():
            _append_rows(self._run_folder.results_path, [
                ResultsRow.of(generation, agent_index, fitness, attempt_result).csv_values()
                for agent_index, (attempt_result, fitness) in enumerate(zip(attempt_results, fitnesses, strict=True))])
            _append_rows(self._run_folder.generation_times_path,
                         [GenerationTimeRow(generation, float(seconds)).csv_values()])
            self._run_folder.generation_path(generation).mkdir(parents=True)
            np.savez_compressed(self._run_folder.controller_logs_path(generation), **{
                CONTROLLER_LOG_KEY_FORMAT.format(agent=agent): controller_log
                for agent, controller_log in enumerate(controller_logs)})
            np.save(self._run_folder.best_genome_path(generation), genomes[best_agent_index(fitnesses)])


@contextmanager
def _ctrl_c_held_back() -> Iterator[None]:
    """Ctrl+C (SIGINT) pressed inside this block is handled as usual once the block ends, not part-way through.

    Signal handlers can be set only in the main thread, which is where training records."""
    ctrl_c_presses = []
    usual_handler = signal.signal(signal.SIGINT, lambda signal_number, frame: ctrl_c_presses.append(frame))
    try:
        yield
    finally:
        signal.signal(signal.SIGINT, usual_handler)
    if ctrl_c_presses and callable(usual_handler):
        usual_handler(signal.SIGINT, ctrl_c_presses[0])


def _append_rows(csv_path: Path, rows: list[tuple]) -> None:
    with csv_path.open("a", newline="") as csv_file:
        csv.writer(csv_file).writerows(rows)
