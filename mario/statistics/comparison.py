"""The comparison of several runs (spec section 13): every run's best and mean fitness on
one chart, and their summaries side by side, first-flag generation first. Each run is
labelled by its run folder's name, which holds its run name and, so that two runs of
one name stay apart, when it started."""

from pathlib import Path

from matplotlib.figure import Figure

from mario.constants.statistics import (
    CHART_SIZE_INCHES,
    COMPARISON_COLUMN_GAP,
    COMPARISON_FILE_NAME,
    COMPARISON_RUN_HEADER,
    BEST_LABEL,
    FITNESS_AXIS_LABEL,
    FITNESS_COMPARISON_CHART_FILE_NAME,
    FITNESS_COMPARISON_CHART_TITLE,
    MEAN_LABEL,
    MEAN_LINE_STYLE,
    RUN_SERIES_LABEL_FORMAT,
    SERIES_COLOURS,
)
from mario.statistics.chart_style import add_legend, name_panel, new_chart, plot_series, save_chart
from mario.statistics.run_statistics import RunStatistics


class Comparison:
    def __init__(self, statistics_of_runs: list[RunStatistics], comparison_folder_path: Path):
        """statistics_of_runs: at most MAX_COMPARED_RUNS, so each gets a colour of its own."""
        self._statistics_of_runs = statistics_of_runs
        self.comparison_folder_path = comparison_folder_path

    def chart(self) -> Figure:
        figure, (panel,) = new_chart(CHART_SIZE_INCHES)
        for run_statistics, colour in zip(self._statistics_of_runs, SERIES_COLOURS):
            run_name = run_statistics.run_folder_path.name
            plot_series(panel, run_statistics.series.generations, run_statistics.series.best_fitness, colour,
                        RUN_SERIES_LABEL_FORMAT.format(run=run_name, series=BEST_LABEL))
            plot_series(panel, run_statistics.series.generations, run_statistics.series.mean_fitness, colour,
                        RUN_SERIES_LABEL_FORMAT.format(run=run_name, series=MEAN_LABEL), linestyle=MEAN_LINE_STYLE)
        name_panel(panel, FITNESS_COMPARISON_CHART_TITLE, FITNESS_AXIS_LABEL)
        add_legend(panel)
        return figure

    def summaries_side_by_side(self) -> str:
        """A table: a header row naming each run, then one row per summary fact, in summary.txt's order."""
        header = [COMPARISON_RUN_HEADER,
                  *(run_statistics.run_folder_path.name for run_statistics in self._statistics_of_runs)]
        entries_by_run = [run_statistics.summary.entries() for run_statistics in self._statistics_of_runs]
        fact_rows = [[label, *(entries[fact][1] for entries in entries_by_run)]
                     for fact, (label, _) in enumerate(entries_by_run[0])]
        table = [header, *fact_rows]
        column_widths = [max(len(row[column]) for row in table) for column in range(len(header))]
        return "".join(COMPARISON_COLUMN_GAP.join(cell.ljust(width) for cell, width in zip(row, column_widths))
                       .rstrip() + "\n" for row in table)

    def write(self) -> None:
        self.comparison_folder_path.mkdir(parents=True, exist_ok=True)
        save_chart(self.chart(), self.comparison_folder_path / FITNESS_COMPARISON_CHART_FILE_NAME)
        (self.comparison_folder_path / COMPARISON_FILE_NAME).write_text(self.summaries_side_by_side())
