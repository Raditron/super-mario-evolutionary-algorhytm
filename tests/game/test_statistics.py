"""py -m mario stats (#31, spec section 13): charts and a summary from run folders.

The run folders here are written by hand, in the layout of spec section 10, so
each test controls exactly what the rows say. Stats reads only results.csv and
generation_times.csv, so the folders hold nothing else.
"""

import csv
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pytest
from matplotlib.backends.backend_agg import FigureCanvasAgg

import mario
from mario.__main__ import main
from mario.constants.statistics import END_REASON_COLOURS, REACHED_FLAG_END_REASON
from mario.modes.stats_mode import StatsMode
from mario.simulation.attempt_result import EndReason
from mario.statistics.comparison_report import ComparisonReport
from mario.statistics.run_statistics_report import RunStatisticsReport

RESULTS_HEADER = ("generation", "agent", "fitness", "end_reason", "furthest_x", "ticks_elapsed",
                  "final_score", "coins_collected")
GENERATION_TIMES_HEADER = ("generation", "seconds")
NOW = datetime(2026, 10, 28, 16, 45)
PNG_SIGNATURE = bytes([0x89]) + b"PNG"
SIX_CHARTS = {"fitness.png", "distance.png", "end_reasons.png", "where_attempts_end.png", "coins_and_time.png",
              "seconds_per_generation.png"}
FLAG_TIME_LINE_LABEL = "fastest flag time (s)"
REPO_ROOT = Path(mario.__file__).parent.parent
# Writes one run folder's statistics in a fresh interpreter, then says whether pyplot was ever loaded.
HEADLESS_PROBE = """import sys
from datetime import datetime
from pathlib import Path
from mario.modes.stats_mode import StatsMode
StatsMode([Path(sys.argv[1])], Path(sys.argv[2]), datetime.now()).run()
print('matplotlib.pyplot' in sys.modules)"""

# Three generations of three agents. The flag is first reached in generation 2;
# the best fitness is generation 3's agent 1; the fastest finish is generation
# 3's agent 2 (2100 ticks = 35 s); the most coins are generation 2's agent 0.
FINISHED_RUN_RESULTS = [
    (1, 0, 12.5, "fell_in_pit", 1100, 400, 100, 1),
    (1, 1, 30.0, "died_to_enemy", 1500, 600, 200, 2),
    (1, 2, 8.0, "stalled", 600, 300, 0, 0),
    (2, 0, 700.0, "died_to_enemy", 2900, 1900, 3000, 7),
    (2, 1, 850.25, "reached_flag", 3170, 2400, 6650, 3),
    (2, 2, 40.0, "stalled", 1600, 700, 0, 2),
    (3, 0, 860.0, "reached_flag", 3170, 2300, 6700, 4),
    (3, 1, 912.5, "reached_flag", 3170, 2200, 7100, 5),
    (3, 2, 900.0, "reached_flag", 3170, 2100, 6800, 6),
]
FINISHED_RUN_GENERATION_TIMES = [(1, 3.5), (2, 4.25), (3, 5.0)]

NO_FINISHER_RESULTS = [
    (1, 0, 12.5, "fell_in_pit", 1100, 400, 100, 1),
    (1, 1, 30.0, "died_to_enemy", 1500, 600, 200, 2),
    (2, 0, 44.0, "timer_ran_out", 1700, 9600, 0, 3),
    (2, 1, 44.0, "stalled", 1700, 900, 0, 0),
]
NO_FINISHER_GENERATION_TIMES = [(1, 1.0), (2, 2.0)]


def write_run_folder(run_folder: Path, results_rows: list[tuple], generation_times: list[tuple]) -> Path:
    run_folder.mkdir(parents=True)
    with (run_folder / "results.csv").open("w", newline="") as results_file:
        csv.writer(results_file).writerows([RESULTS_HEADER, *results_rows])
    with (run_folder / "generation_times.csv").open("w", newline="") as times_file:
        csv.writer(times_file).writerows([GENERATION_TIMES_HEADER, *generation_times])
    return run_folder


def summary_lines(run_folder: Path) -> list[str]:
    return (run_folder / "statistics" / "summary.txt").read_text().splitlines()


def line_labels(figure) -> set[str]:
    return {line.get_label() for axes in figure.axes for line in axes.get_lines()}


def test_the_summary_of_one_run_folder_is_computed_from_its_rows(tmp_path):
    run_folder = write_run_folder(tmp_path / "runs" / "2026-10-28_09-30_finished",
                                  FINISHED_RUN_RESULTS, FINISHED_RUN_GENERATION_TIMES)
    StatsMode([run_folder], tmp_path / "runs", NOW).run()
    assert summary_lines(run_folder) == [
        "First generation to reach the flag: 2",
        "Best fitness: 912.50 (generation 3, agent 1)",
        "Fastest finish: 35.00 s, 2100 ticks (generation 3, agent 2)",
        "Most coins: 7 (generation 2, agent 0)",
        "Total run time: 12.75 s",
    ]


def test_a_run_with_no_finishers_never_reached_the_flag(tmp_path):
    """On a tie (here the best fitness, 44.0), the fact belongs to the earliest row: the lowest agent."""
    run_folder = write_run_folder(tmp_path / "runs" / "2026-10-28_10-00_unfinished",
                                  NO_FINISHER_RESULTS, NO_FINISHER_GENERATION_TIMES)
    StatsMode([run_folder], tmp_path / "runs", NOW).run()
    assert summary_lines(run_folder) == [
        "First generation to reach the flag: never",
        "Best fitness: 44.00 (generation 2, agent 0)",
        "Fastest finish: never",
        "Most coins: 3 (generation 2, agent 0)",
        "Total run time: 3.00 s",
    ]


def test_one_run_folder_gets_all_six_charts_and_its_summary(tmp_path):
    run_folder = write_run_folder(tmp_path / "runs" / "2026-10-28_09-30_finished",
                                  FINISHED_RUN_RESULTS, FINISHED_RUN_GENERATION_TIMES)
    StatsMode([run_folder], tmp_path / "runs", NOW).run()
    statistics_folder = run_folder / "statistics"
    assert {path.name for path in statistics_folder.iterdir()} == SIX_CHARTS | {"summary.txt"}
    assert all((statistics_folder / chart).read_bytes().startswith(PNG_SIGNATURE) for chart in SIX_CHARTS)


def test_a_rerun_overwrites_the_earlier_statistics(tmp_path):
    run_folder = write_run_folder(tmp_path / "runs" / "2026-10-28_09-30_finished",
                                  FINISHED_RUN_RESULTS, FINISHED_RUN_GENERATION_TIMES)
    StatsMode([run_folder], tmp_path / "runs", NOW).run()
    (run_folder / "statistics" / "summary.txt").write_text("stale")
    StatsMode([run_folder], tmp_path / "runs", NOW).run()
    assert summary_lines(run_folder)[0] == "First generation to reach the flag: 2"


def test_the_flag_time_line_is_drawn_only_for_a_run_with_finishers(tmp_path):
    finished_run = write_run_folder(tmp_path / "finished", FINISHED_RUN_RESULTS, FINISHED_RUN_GENERATION_TIMES)
    unfinished_run = write_run_folder(tmp_path / "unfinished", NO_FINISHER_RESULTS, NO_FINISHER_GENERATION_TIMES)
    assert FLAG_TIME_LINE_LABEL in line_labels(RunStatisticsReport(finished_run).charts()["coins_and_time.png"])
    assert FLAG_TIME_LINE_LABEL not in line_labels(RunStatisticsReport(unfinished_run).charts()["coins_and_time.png"])


def test_the_distance_chart_marks_the_warp_pipe_and_the_flagpole_of_the_level(tmp_path):
    """World 1-1's warp pipe is at column 57 and its flagpole at column 198 (docs/research/world-1-1-layout.md)."""
    run_folder = write_run_folder(tmp_path / "finished", FINISHED_RUN_RESULTS, FINISHED_RUN_GENERATION_TIMES)
    (panel,) = RunStatisticsReport(run_folder).charts()["distance.png"].axes
    assert {text.get_text() for text in panel.texts} == {"warp pipe (column 57)", "flag (column 198)"}


def test_a_run_with_no_finishers_still_gets_all_six_charts(tmp_path):
    run_folder = write_run_folder(tmp_path / "unfinished", NO_FINISHER_RESULTS, NO_FINISHER_GENERATION_TIMES)
    StatsMode([run_folder], tmp_path / "runs", NOW).run()
    assert SIX_CHARTS <= {path.name for path in (run_folder / "statistics").iterdir()}


FINISHED_RUN_NAME = "2026-10-28_09-30_finished"
UNFINISHED_RUN_NAME = "2026-10-28_10-00_unfinished"
COMPARISON_FOLDER = Path("comparisons") / "2026-10-28_16-45"


def two_run_folders(runs_root: Path) -> list[Path]:
    return [write_run_folder(runs_root / FINISHED_RUN_NAME, FINISHED_RUN_RESULTS, FINISHED_RUN_GENERATION_TIMES),
            write_run_folder(runs_root / UNFINISHED_RUN_NAME, NO_FINISHER_RESULTS, NO_FINISHER_GENERATION_TIMES)]


def table_cells(text: str) -> list[list[str]]:
    """A side-by-side table's rows, each split into its cells (parted by two spaces or more)."""
    return [[cell for cell in re.split(r" {2,}", line.strip())] for line in text.splitlines()]


def test_several_run_folders_get_a_comparison_named_after_when_it_was_made(tmp_path):
    runs_root = tmp_path / "runs"
    StatsMode(two_run_folders(runs_root), runs_root, NOW).run()
    comparison_folder = runs_root / COMPARISON_FOLDER
    assert {path.name for path in comparison_folder.iterdir()} == {"fitness_comparison.png", "comparison.txt"}
    assert (comparison_folder / "fitness_comparison.png").read_bytes().startswith(PNG_SIGNATURE)


def test_the_comparison_puts_the_summaries_side_by_side_first_flag_generation_first(tmp_path):
    runs_root = tmp_path / "runs"
    StatsMode(two_run_folders(runs_root), runs_root, NOW).run()
    assert table_cells((runs_root / COMPARISON_FOLDER / "comparison.txt").read_text()) == [
        ["Run", FINISHED_RUN_NAME, UNFINISHED_RUN_NAME],
        ["First generation to reach the flag", "2", "never"],
        ["Best fitness", "912.50 (generation 3, agent 1)", "44.00 (generation 2, agent 0)"],
        ["Fastest finish", "35.00 s, 2100 ticks (generation 3, agent 2)", "never"],
        ["Most coins", "7 (generation 2, agent 0)", "3 (generation 2, agent 0)"],
        ["Total run time", "12.75 s", "3.00 s"],
    ]


def test_the_comparison_chart_draws_every_runs_best_and_mean_fitness_labelled_by_run(tmp_path):
    runs_root = tmp_path / "runs"
    comparison = ComparisonReport([RunStatisticsReport(folder) for folder in two_run_folders(runs_root)],
                                  runs_root / COMPARISON_FOLDER)
    assert line_labels(comparison.chart()) == {f"{FINISHED_RUN_NAME} best", f"{FINISHED_RUN_NAME} mean",
                                               f"{UNFINISHED_RUN_NAME} best", f"{UNFINISHED_RUN_NAME} mean"}


def test_a_comparison_leaves_each_run_folder_as_it_was(tmp_path):
    runs_root = tmp_path / "runs"
    run_folders = two_run_folders(runs_root)
    StatsMode(run_folders, runs_root, NOW).run()
    assert all({path.name for path in folder.iterdir()} == {"results.csv", "generation_times.csv"}
               for folder in run_folders)


def test_a_folder_that_is_not_a_run_folder_says_so(tmp_path):
    with pytest.raises(SystemExit, match="not a run folder"):
        StatsMode([tmp_path / "missing"], tmp_path / "runs", NOW).run()


def test_a_run_folder_with_no_generation_yet_says_so(tmp_path):
    run_folder = write_run_folder(tmp_path / "runs" / "2026-10-28_11-00_new", [], [])
    with pytest.raises(SystemExit, match="no generation"):
        StatsMode([run_folder], tmp_path / "runs", NOW).run()


def test_a_run_folder_with_an_unknown_end_reason_says_so(tmp_path):
    run_folder = write_run_folder(tmp_path / "runs" / "2026-10-28_11-30_odd",
                                  [(1, 0, 12.5, "teleported", 1100, 400, 100, 1)], [(1, 1.0)])
    with pytest.raises(SystemExit, match="can't be read.*teleported"):
        StatsMode([run_folder], tmp_path / "runs", NOW).run()
    assert not (run_folder / "statistics").exists()


def test_more_runs_than_there_are_series_colours_are_not_compared(tmp_path):
    """Each run's colour is its own, never cycled: eight colours, so at most eight runs."""
    runs_root = tmp_path / "runs"
    run_folders = [write_run_folder(runs_root / f"2026-10-28_09-3{index}_run", FINISHED_RUN_RESULTS,
                                    FINISHED_RUN_GENERATION_TIMES) for index in range(9)]
    with pytest.raises(SystemExit, match="at most 8 runs"):
        StatsMode(run_folders, runs_root, NOW).run()
    assert not (runs_root / "comparisons").exists()


def test_py_m_mario_stats_writes_one_run_folders_statistics(tmp_path, monkeypatch):
    runs_root = tmp_path / "runs"
    run_folder = write_run_folder(runs_root / FINISHED_RUN_NAME, FINISHED_RUN_RESULTS, FINISHED_RUN_GENERATION_TIMES)
    monkeypatch.setattr(sys, "argv", ["mario", "stats", str(run_folder)])
    main(runs_root)
    assert summary_lines(run_folder)[0] == "First generation to reach the flag: 2"


def test_py_m_mario_stats_with_two_run_folders_writes_their_comparison_into_the_runs_folder(tmp_path, monkeypatch):
    runs_root = tmp_path / "runs"
    monkeypatch.setattr(sys, "argv", ["mario", "stats", *map(str, two_run_folders(runs_root))])
    main(runs_root)
    (comparison_folder,) = (runs_root / "comparisons").iterdir()
    assert (comparison_folder / "comparison.txt").is_file()


def test_stats_writes_its_charts_without_ever_loading_pyplot(tmp_path):
    """pyplot picks a GUI backend and keeps global figures; stats must run headless, as training does."""
    run_folder = write_run_folder(tmp_path / "runs" / FINISHED_RUN_NAME, FINISHED_RUN_RESULTS,
                                  FINISHED_RUN_GENERATION_TIMES)
    probe = subprocess.run([sys.executable, "-c", HEADLESS_PROBE, str(run_folder), str(tmp_path / "runs")],
                           capture_output=True, text=True, check=True, cwd=REPO_ROOT)
    assert probe.stdout.strip().splitlines()[-1] == "False"
    assert SIX_CHARTS <= {path.name for path in (run_folder / "statistics").iterdir()}


def test_every_chart_is_drawn_on_the_agg_canvas(tmp_path):
    runs_root = tmp_path / "runs"
    run_statistics = [RunStatisticsReport(folder) for folder in two_run_folders(runs_root)]
    figures = [*run_statistics[0].charts().values(),
               ComparisonReport(run_statistics, runs_root / COMPARISON_FOLDER).chart()]
    assert all(type(figure.canvas) is FigureCanvasAgg for figure in figures)


def test_statistics_knows_every_end_reason_without_importing_the_simulation():
    """It reads end_reason as text, so its names for them must be EndReason's own."""
    assert list(END_REASON_COLOURS) == [end_reason.value for end_reason in EndReason]
    assert REACHED_FLAG_END_REASON == EndReason.REACHED_FLAG
