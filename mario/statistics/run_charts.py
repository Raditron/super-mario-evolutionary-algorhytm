"""The six charts of one run (spec section 13), drawn from its GenerationSeries."""

from matplotlib.colors import LinearSegmentedColormap
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator

from mario.constants.level import TILE_SIZE_PIXELS
from mario.constants.statistics import (
    ATTEMPTS_COLOUR_BAR_LABEL,
    BEST_LABEL,
    BEST_SERIES_COLOUR,
    CHART_MUTED_TEXT_COLOUR,
    CHART_SIZE_INCHES,
    CHART_SURFACE_COLOUR,
    COINS_AND_TIME_CHART_FILE_NAME,
    COINS_AND_TIME_CHART_TITLE,
    COINS_AXIS_LABEL,
    DISTANCE_CHART_FILE_NAME,
    DISTANCE_CHART_TITLE,
    END_REASON_COLOURS,
    END_REASONS_CHART_FILE_NAME,
    END_REASONS_CHART_TITLE,
    FITNESS_AXIS_LABEL,
    FITNESS_BAND_COLOUR,
    FITNESS_BAND_LABEL,
    FITNESS_BAND_OPACITY,
    FITNESS_CHART_FILE_NAME,
    FITNESS_CHART_TITLE,
    FLAG_TIME_AXIS_LABEL,
    FLAG_TIME_LABEL,
    FLAG_TIME_MARKER,
    FLAG_TIME_MARKER_SIZE_POINTS,
    FLAG_TIME_SERIES_COLOUR,
    FLAGPOLE_LABEL_FORMAT,
    FURTHEST_X_AXIS_LABEL,
    HEATMAP_COLOUR_MAP_NAME,
    HEATMAP_CELL_HALF_WIDTH_GENERATIONS,
    HEATMAP_COLOURS,
    MEAN_LABEL,
    MEAN_LINE_STYLE,
    MEAN_SERIES_COLOUR,
    MEDIAN_LABEL,
    MEDIAN_SERIES_COLOUR,
    NO_FINISHER_NOTE,
    NO_FINISHER_NOTE_POSITION,
    REFERENCE_LINE_STYLE,
    REFERENCE_LINE_WIDTH_POINTS,
    SECONDS_AXIS_LABEL,
    SECONDS_PER_GENERATION_CHART_FILE_NAME,
    SECONDS_PER_GENERATION_CHART_TITLE,
    SECONDS_SERIES_COLOUR,
    SHARE_OF_ATTEMPTS_AXIS_LABEL,
    STACKED_AREA_GAP_WIDTH_POINTS,
    STACKED_PANELS_CHART_SIZE_INCHES,
    WARP_PIPE_LABEL_FORMAT,
    WHERE_ATTEMPTS_END_CHART_FILE_NAME,
    WHERE_ATTEMPTS_END_CHART_TITLE,
)
from mario.level.static_level import PipeDestination, StaticLevel
from mario.statistics.chart_style import (
    add_legend,
    add_legend_beside_stack,
    muted_label_style,
    name_panel,
    new_chart,
    plot_series,
)
from mario.statistics.generation_series import GenerationSeries


class RunCharts:
    def __init__(self, series: GenerationSeries, level: StaticLevel):
        """level: where the distance chart's landmarks, the warp pipe and the flagpole, stand."""
        self._series = series
        self._level = level

    def figures(self) -> dict[str, Figure]:
        """Each chart's figure, keyed by its file name."""
        return {
            FITNESS_CHART_FILE_NAME: self._fitness(),
            DISTANCE_CHART_FILE_NAME: self._distance(),
            END_REASONS_CHART_FILE_NAME: self._end_reasons(),
            WHERE_ATTEMPTS_END_CHART_FILE_NAME: self._where_attempts_end(),
            COINS_AND_TIME_CHART_FILE_NAME: self._coins_and_time(),
            SECONDS_PER_GENERATION_CHART_FILE_NAME: self._seconds_per_generation(),
        }

    def _fitness(self) -> Figure:
        series = self._series
        figure, (panel,) = new_chart(CHART_SIZE_INCHES)
        panel.fill_between(series.generations, series.fitness_band_low, series.fitness_band_high,
                           color=FITNESS_BAND_COLOUR, alpha=FITNESS_BAND_OPACITY, linewidth=0,
                           label=FITNESS_BAND_LABEL)
        plot_series(panel, series.generations, series.best_fitness, BEST_SERIES_COLOUR, BEST_LABEL)
        plot_series(panel, series.generations, series.mean_fitness, MEAN_SERIES_COLOUR, MEAN_LABEL)
        plot_series(panel, series.generations, series.median_fitness, MEDIAN_SERIES_COLOUR, MEDIAN_LABEL)
        name_panel(panel, FITNESS_CHART_TITLE, FITNESS_AXIS_LABEL)
        add_legend(panel)
        return figure

    def _distance(self) -> Figure:
        series = self._series
        figure, (panel,) = new_chart(CHART_SIZE_INCHES)
        plot_series(panel, series.generations, series.best_furthest_x, BEST_SERIES_COLOUR, BEST_LABEL)
        plot_series(panel, series.generations, series.median_furthest_x, MEDIAN_SERIES_COLOUR, MEDIAN_LABEL)
        warp_pipe_column = next(pipe.left_column for pipe in self._level.pipes
                                if pipe.leads_to is PipeDestination.BONUS_ROOM)
        for column, label_format in ((warp_pipe_column, WARP_PIPE_LABEL_FORMAT),
                                     (self._level.flagpole_column, FLAGPOLE_LABEL_FORMAT)):
            landmark_x = column * TILE_SIZE_PIXELS
            label = label_format.format(column=column)
            panel.axhline(landmark_x, color=CHART_MUTED_TEXT_COLOUR, linestyle=REFERENCE_LINE_STYLE,
                          linewidth=REFERENCE_LINE_WIDTH_POINTS)
            panel.annotate(label, (0, landmark_x), xycoords=("axes fraction", "data"), va="bottom",
                           **muted_label_style())
        name_panel(panel, DISTANCE_CHART_TITLE, FURTHEST_X_AXIS_LABEL)
        add_legend(panel)
        return figure

    def _end_reasons(self) -> Figure:
        series = self._series
        figure, (panel,) = new_chart(CHART_SIZE_INCHES)
        panel.stackplot(series.generations, *series.end_reason_shares.values(),
                        labels=list(series.end_reason_shares), colors=list(END_REASON_COLOURS.values()),
                        edgecolor=CHART_SURFACE_COLOUR, linewidth=STACKED_AREA_GAP_WIDTH_POINTS)
        panel.set_ylim(0, 1)
        name_panel(panel, END_REASONS_CHART_TITLE, SHARE_OF_ATTEMPTS_AXIS_LABEL)
        add_legend_beside_stack(panel)
        return figure

    def _where_attempts_end(self) -> Figure:
        series = self._series
        figure, (panel,) = new_chart(CHART_SIZE_INCHES)
        generation_edges = [*(series.generations - HEATMAP_CELL_HALF_WIDTH_GENERATIONS),
                            series.generations[-1] + HEATMAP_CELL_HALF_WIDTH_GENERATIONS]
        colour_map = LinearSegmentedColormap.from_list(HEATMAP_COLOUR_MAP_NAME, HEATMAP_COLOURS)
        heatmap = panel.pcolormesh(generation_edges, series.heatmap_bin_edges, series.furthest_x_counts,
                                   cmap=colour_map)
        colour_bar = figure.colorbar(heatmap, ax=panel)
        colour_bar.locator = MaxNLocator(integer=True)
        colour_bar.update_ticks()
        colour_bar.set_label(ATTEMPTS_COLOUR_BAR_LABEL, **muted_label_style())
        panel.grid(False)
        name_panel(panel, WHERE_ATTEMPTS_END_CHART_TITLE, FURTHEST_X_AXIS_LABEL)
        return figure

    def _coins_and_time(self) -> Figure:
        """Coins above, the fastest flag time below: two measures, so two panels, not two scales on one."""
        series = self._series
        figure, (coins_panel, flag_time_panel) = new_chart(STACKED_PANELS_CHART_SIZE_INCHES, panel_count=2)
        plot_series(coins_panel, series.generations, series.best_coins, BEST_SERIES_COLOUR, BEST_LABEL)
        plot_series(coins_panel, series.generations, series.mean_coins, MEAN_SERIES_COLOUR, MEAN_LABEL,
                    linestyle=MEAN_LINE_STYLE)
        name_panel(coins_panel, COINS_AND_TIME_CHART_TITLE, COINS_AXIS_LABEL)
        add_legend(coins_panel)
        if series.anyone_reached_the_flag:
            plot_series(flag_time_panel, series.generations, series.fastest_flag_seconds, FLAG_TIME_SERIES_COLOUR,
                        FLAG_TIME_LABEL, marker=FLAG_TIME_MARKER, markersize=FLAG_TIME_MARKER_SIZE_POINTS)
            add_legend(flag_time_panel)
        else:
            flag_time_panel.text(*NO_FINISHER_NOTE_POSITION, NO_FINISHER_NOTE, transform=flag_time_panel.transAxes,
                                 ha="center", va="center", **muted_label_style())
        flag_time_panel.set_ylabel(FLAG_TIME_AXIS_LABEL, **muted_label_style())
        return figure

    def _seconds_per_generation(self) -> Figure:
        series = self._series
        figure, (panel,) = new_chart(CHART_SIZE_INCHES)
        plot_series(panel, series.timed_generations, series.seconds_per_generation, SECONDS_SERIES_COLOUR)
        name_panel(panel, SECONDS_PER_GENERATION_CHART_TITLE, SECONDS_AXIS_LABEL)
        return figure
