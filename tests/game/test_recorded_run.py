"""Reading a run folder back for replay (#28, spec sections 10 and 11): which
generations it holds, each one's best agent, and any agent's Controller log.

The run folders here are written by hand, in the layout of spec section 10, so
each test controls exactly what the folder holds.
"""

import csv
from pathlib import Path

import numpy as np
import pytest

from mario.recording.recorded_run import RecordedRun
from mario.recording.results_row import ResultsRow
from mario.simulation.attempt_result import EndReason

RESULTS_HEADER = ("generation", "agent", "fitness", "end_reason", "furthest_x", "ticks_elapsed",
                  "final_score", "coins_collected")


def write_run_folder(run_folder: Path, results_rows: list[tuple], controller_logs_by_generation: dict) -> Path:
    """A run folder with these results.csv rows and, per generation, these Controller logs."""
    run_folder.mkdir()
    with (run_folder / "results.csv").open("w", newline="") as results_file:
        csv.writer(results_file).writerows([RESULTS_HEADER, *results_rows])
    for generation, controller_logs in controller_logs_by_generation.items():
        generation_folder = run_folder / "generations" / f"{generation:04d}"
        generation_folder.mkdir(parents=True)
        np.savez_compressed(generation_folder / "controller_logs.npz",
                            **{str(agent): np.array(log, dtype=np.uint8) for agent, log in enumerate(controller_logs)})
    return run_folder


def test_the_last_recorded_generation_is_the_highest_numbered_generation_folder(tmp_path):
    run_folder = write_run_folder(tmp_path / "run", [
        (1, 0, 1.0, "stalled", 40, 180, 0, 0),
        (2, 0, 1.0, "stalled", 40, 180, 0, 0),
        (3, 0, 1.0, "stalled", 40, 180, 0, 0),
    ], {1: [[0]], 2: [[0]], 3: [[0]]})
    assert RecordedRun(run_folder).last_generation() == 3


def test_a_generation_whose_folder_was_never_written_is_not_recorded(tmp_path):
    """The generation folder is the last thing written, so a generation is recorded once it exists."""
    run_folder = write_run_folder(tmp_path / "run", [
        (1, 0, 1.0, "stalled", 40, 180, 0, 0),
        (2, 0, 1.0, "stalled", 40, 180, 0, 0),
    ], {1: [[0]]})
    recorded_run = RecordedRun(run_folder)
    assert recorded_run.last_generation() == 1
    with pytest.raises(LookupError, match="generation 2"):
        recorded_run.best_agent(2)


def test_a_run_folder_with_no_generation_yet_says_so(tmp_path):
    run_folder = write_run_folder(tmp_path / "run", [], {})
    with pytest.raises(LookupError, match="no generation"):
        RecordedRun(run_folder).last_generation()


def test_a_folder_that_is_not_a_run_folder_says_so(tmp_path):
    with pytest.raises(LookupError, match="not a run folder"):
        RecordedRun(tmp_path / "missing").last_generation()


def test_the_best_agent_has_the_highest_fitness_of_its_generation(tmp_path):
    run_folder = write_run_folder(tmp_path / "run", [
        (1, 0, 900.5, "reached_flag", 3170, 2400, 6650, 3),
        (2, 0, 10.0, "fell_in_pit", 600, 300, 0, 0),
        (2, 1, 55.25, "died_to_enemy", 812, 410, 100, 1),
        (2, 2, 30.0, "stalled", 500, 380, 0, 0),
    ], {1: [[0]], 2: [[0], [0], [0]]})
    assert RecordedRun(run_folder).best_agent(2) == ResultsRow(
        generation=2, agent_index=1, fitness=55.25, end_reason=EndReason.DIED_TO_ENEMY, furthest_x=812,
        ticks_elapsed=410, final_score=100, coins_collected=1)


def test_on_a_tie_the_best_agent_is_the_one_with_the_lowest_index(tmp_path):
    run_folder = write_run_folder(tmp_path / "run", [
        (1, 0, 3.0, "stalled", 40, 180, 0, 0),
        (1, 1, 7.0, "stalled", 70, 180, 0, 0),
        (1, 2, 7.0, "stalled", 70, 180, 0, 0),
    ], {1: [[0], [0], [0]]})
    assert RecordedRun(run_folder).best_agent(1).agent_index == 1


def test_an_agents_controller_log_is_read_back_by_its_index(tmp_path):
    run_folder = write_run_folder(tmp_path / "run", [
        (1, 0, 1.0, "stalled", 40, 3, 0, 0),
        (1, 1, 2.0, "stalled", 40, 4, 0, 0),
    ], {1: [[1, 2, 3], [4, 5, 6, 7]]})
    controller_log = RecordedRun(run_folder).controller_log(1, 1)
    assert controller_log.dtype == np.uint8
    assert controller_log.tolist() == [4, 5, 6, 7]
