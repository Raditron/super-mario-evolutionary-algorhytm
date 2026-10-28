"""One run folder's statistics (spec section 13): its six charts and summary.txt,
written into <run-folder>/statistics/, overwriting any earlier ones, from its rows alone."""

from pathlib import Path

from matplotlib.figure import Figure

from mario.constants.statistics import STATISTICS_FOLDER_NAME, SUMMARY_FILE_NAME
from mario.level.static_level import StaticLevel
from mario.recording.recorded_run import RecordedRun
from mario.statistics.chart_style import save_chart
from mario.statistics.generation_series import GenerationSeries
from mario.statistics.run_charts import RunCharts
from mario.statistics.run_summary import RunSummary


class RunStatisticsReport:
    def __init__(self, run_folder_path: Path):
        """Reads the run folder's rows. Raises LookupError if it isn't a run folder or has no generation yet."""
        self.run_folder_path = run_folder_path
        recorded_run = RecordedRun(run_folder_path)
        results_rows = recorded_run.results_rows()
        if not results_rows:
            raise LookupError(f"{run_folder_path} has no generation recorded yet")
        generation_time_rows = recorded_run.generation_time_rows()
        self.summary = RunSummary.of(results_rows, generation_time_rows)
        self.series = GenerationSeries.of(results_rows, generation_time_rows)

    @property
    def statistics_folder_path(self) -> Path:
        return self.run_folder_path / STATISTICS_FOLDER_NAME

    def charts(self) -> dict[str, Figure]:
        """The six charts, keyed by their file names."""
        return RunCharts(self.series, StaticLevel.load_world_1_1()).figures()

    def write(self) -> None:
        self.statistics_folder_path.mkdir(exist_ok=True)
        for file_name, figure in self.charts().items():
            save_chart(figure, self.statistics_folder_path / file_name)
        (self.statistics_folder_path / SUMMARY_FILE_NAME).write_text(self.summary.text())
