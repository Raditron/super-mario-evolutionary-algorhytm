"""py -m mario stats <run-folder> [more run folders...] (spec sections 2 and 13).

One run folder: its charts and summary.txt, in <run-folder>/statistics/. Several:
their comparison, in runs/comparisons/YYYY-MM-DD_HH-MM/, leaving each run folder
as it was. It reads only results.csv and generation_times.csv and writes nothing
back into them, so it works on a run stopped early, and it never imports the
user's neuroevolution package.
"""

from datetime import datetime
from pathlib import Path

from mario.constants.statistics import COMPARISON_FOLDER_TIMESTAMP_FORMAT, COMPARISONS_FOLDER_NAME, MAX_COMPARED_RUNS
from mario.statistics.comparison import Comparison
from mario.statistics.run_statistics import RunStatistics

WROTE_STATISTICS_MESSAGE = "Wrote the statistics of {run_folder} to {statistics_folder}."
WROTE_COMPARISON_MESSAGE = "Wrote the comparison of {run_count} runs to {comparison_folder}."
CANT_WRITE_STATISTICS_MESSAGE = "Can't write statistics: {problem}."
TOO_MANY_RUNS_PROBLEM = f"at most {MAX_COMPARED_RUNS} runs can be compared at once"
# A row whose value isn't of its column's kind: an end_reason that isn't an EndReason, say.
UNREADABLE_ROW_PROBLEM = "a row of {run_folder} can't be read ({error})"


class StatsMode:
    def __init__(self, run_folder_paths: list[Path], runs_root: Path, now: datetime):
        """run_folder_paths: one or more. runs_root: where the comparisons folder is made;
        now: when, which names the comparison's folder."""
        self._run_folder_paths = run_folder_paths
        self._runs_root = runs_root
        self._now = now

    def run(self) -> None:
        """Exits with a message, writing nothing, if any folder can't be read as a run with a generation."""
        if len(self._run_folder_paths) > MAX_COMPARED_RUNS:
            raise SystemExit(CANT_WRITE_STATISTICS_MESSAGE.format(problem=TOO_MANY_RUNS_PROBLEM))
        statistics_of_runs = [_read_run(run_folder_path) for run_folder_path in self._run_folder_paths]
        if len(statistics_of_runs) == 1:
            statistics_of_runs[0].write()
            print(WROTE_STATISTICS_MESSAGE.format(run_folder=statistics_of_runs[0].run_folder_path,
                                                  statistics_folder=statistics_of_runs[0].statistics_folder_path))
            return
        comparison_folder_path = (self._runs_root / COMPARISONS_FOLDER_NAME
                                  / self._now.strftime(COMPARISON_FOLDER_TIMESTAMP_FORMAT))
        comparison = Comparison(statistics_of_runs, comparison_folder_path)
        comparison.write()
        print(WROTE_COMPARISON_MESSAGE.format(run_count=len(statistics_of_runs),
                                              comparison_folder=comparison_folder_path))


def _read_run(run_folder_path: Path) -> RunStatistics:
    """Exits with a message if the folder isn't a run folder, has no generation yet, or has a row it can't read."""
    try:
        return RunStatistics(run_folder_path)
    except LookupError as problem:
        raise SystemExit(CANT_WRITE_STATISTICS_MESSAGE.format(problem=problem.args[0])) from None
    except ValueError as error:
        problem = UNREADABLE_ROW_PROBLEM.format(run_folder=run_folder_path, error=error)
        raise SystemExit(CANT_WRITE_STATISTICS_MESSAGE.format(problem=problem)) from None
