"""Statistics from run folders (#12, #31, spec section 13): where they are written, the summary's
lines, and the charts' files, sizes, colours and labels."""

from mario.constants.level import LEVEL_WIDTH_TILES, TILE_SIZE_PIXELS

# One run folder's charts and summary go in this folder inside it, overwritten on a re-run.
STATISTICS_FOLDER_NAME = "statistics"
SUMMARY_FILE_NAME = "summary.txt"

# The end_reason of an attempt that touched the flagpole (EndReason.REACHED_FLAG):
# statistics reads it from results.csv and never imports the simulation.
REACHED_FLAG_END_REASON = "reached_flag"

# --- The summary --------------------------------------------------------------------------

# Each line of summary.txt is a label and its value.
SUMMARY_LINE_FORMAT = "{label}: {value}"
FIRST_FLAG_GENERATION_LABEL = "First generation to reach the flag"
BEST_FITNESS_LABEL = "Best fitness"
FASTEST_FINISH_LABEL = "Fastest finish"
MOST_COINS_LABEL = "Most coins"
TOTAL_RUN_TIME_LABEL = "Total run time"
# The value of the first-flag generation and the fastest finish when no agent reached the flag.
NEVER_REACHED_THE_FLAG_TEXT = "never"
# Which agent a value belongs to.
AGENT_OF_A_VALUE_FORMAT = "{value} (generation {generation}, agent {agent})"
SUMMARY_FITNESS_DECIMALS = 2
SUMMARY_SECONDS_DECIMALS = 2
SECONDS_FORMAT = "{seconds:.{decimals}f} s"
FINISH_TIME_FORMAT = "{seconds}, {ticks} ticks"

# --- The six charts of one run (spec section 13) -------------------------------------------------

FITNESS_CHART_FILE_NAME = "fitness.png"
DISTANCE_CHART_FILE_NAME = "distance.png"
END_REASONS_CHART_FILE_NAME = "end_reasons.png"
WHERE_ATTEMPTS_END_CHART_FILE_NAME = "where_attempts_end.png"
COINS_AND_TIME_CHART_FILE_NAME = "coins_and_time.png"
SECONDS_PER_GENERATION_CHART_FILE_NAME = "seconds_per_generation.png"

# Every chart is drawn at this size and resolution; the coins-and-time chart's two
# stacked panels (coins above, flag time below: two measures never share one axis) at its own.
CHART_SIZE_INCHES = (9.0, 5.0)
STACKED_PANELS_CHART_SIZE_INCHES = (9.0, 7.0)
CHART_DPI = 150

# The fitness chart's shaded band runs between these percentiles of each generation's fitness.
FITNESS_BAND_LOW_PERCENTILE = 10
FITNESS_BAND_HIGH_PERCENTILE = 90

# The distance chart's dashed lines: the warp pipe and the flagpole, by their level column
# (docs/research/world-1-1-layout.md: pipe at columns 57-58, flagpole at column 198).
WARP_PIPE_COLUMN = 57
FLAGPOLE_COLUMN = 198

# The heatmap counts attempts by furthest_x in bins of this many pixels: one level column each.
HEATMAP_BIN_WIDTH_PIXELS = TILE_SIZE_PIXELS
HEATMAP_LEVEL_WIDTH_PIXELS = LEVEL_WIDTH_TILES * TILE_SIZE_PIXELS
# Each generation's heatmap cell reaches this far either side of its generation number.
HEATMAP_CELL_HALF_WIDTH_GENERATIONS = 0.5

# --- Colours: the dataviz reference palette, light mode ----------------------------------------------

CHART_SURFACE_COLOUR = "#fcfcfb"
CHART_TEXT_COLOUR = "#0b0b0b"
CHART_MUTED_TEXT_COLOUR = "#52514e"
CHART_GRID_COLOUR = "#e4e3df"
# Categorical series colours, given out in this fixed order and never cycled.
SERIES_COLOURS = ("#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948")
BEST_SERIES_COLOUR = SERIES_COLOURS[0]
MEAN_SERIES_COLOUR = SERIES_COLOURS[1]
MEDIAN_SERIES_COLOUR = SERIES_COLOURS[2]
FLAG_TIME_SERIES_COLOUR = SERIES_COLOURS[0]
SECONDS_SERIES_COLOUR = SERIES_COLOURS[0]
FITNESS_BAND_COLOUR = SERIES_COLOURS[0]
FITNESS_BAND_OPACITY = 0.18
# Each end_reason (EndReason's values) with its colour, stacked in this order.
END_REASON_COLOURS = {
    "died_to_enemy": SERIES_COLOURS[0],
    "fell_in_pit": SERIES_COLOURS[1],
    "stalled": SERIES_COLOURS[2],
    "timer_ran_out": SERIES_COLOURS[3],
    "reached_flag": SERIES_COLOURS[4],
}
# The heatmap's one-hue ramp, from no attempts (lightest) to the most (darkest).
HEATMAP_COLOURS = ("#fcfcfb", "#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b")
HEATMAP_COLOUR_MAP_NAME = "attempts"

# --- Marks -------------------------------------------------------------------------------------

SERIES_LINE_WIDTH_POINTS = 1.75
REFERENCE_LINE_WIDTH_POINTS = 1.0
REFERENCE_LINE_STYLE = "--"
MEAN_LINE_STYLE = "--"
# Stacked areas are parted by a thin line of the surface colour.
STACKED_AREA_GAP_WIDTH_POINTS = 1.0
# Generations with a finisher are marked, so a lone one still shows.
FLAG_TIME_MARKER = "o"
FLAG_TIME_MARKER_SIZE_POINTS = 4.0
TITLE_FONT_SIZE_POINTS = 12
# A legend beside its panel starts at the panel's top-right corner (in fractions of the panel).
LEGEND_BESIDE_PANEL_ANCHOR = (1.0, 1.0)
LABEL_FONT_SIZE_POINTS = 10

# --- Titles and labels ----------------------------------------------------------------------------

GENERATION_AXIS_LABEL = "generation"
FITNESS_CHART_TITLE = "Fitness per generation"
FITNESS_AXIS_LABEL = "fitness"
BEST_LABEL = "best"
MEAN_LABEL = "mean"
MEDIAN_LABEL = "median"
FITNESS_BAND_LABEL = f"{FITNESS_BAND_LOW_PERCENTILE}th-{FITNESS_BAND_HIGH_PERCENTILE}th percentile"
DISTANCE_CHART_TITLE = "Distance per generation"
FURTHEST_X_AXIS_LABEL = "furthest_x (px)"
WARP_PIPE_LABEL = f"warp pipe (column {WARP_PIPE_COLUMN})"
FLAGPOLE_LABEL = f"flag (column {FLAGPOLE_COLUMN})"
END_REASONS_CHART_TITLE = "How attempts ended"
SHARE_OF_ATTEMPTS_AXIS_LABEL = "share of attempts"
WHERE_ATTEMPTS_END_CHART_TITLE = "Where attempts end"
ATTEMPTS_COLOUR_BAR_LABEL = "attempts"
COINS_AND_TIME_CHART_TITLE = "Coins and time"
COINS_AXIS_LABEL = "coins collected"
FLAG_TIME_AXIS_LABEL = "seconds"
FLAG_TIME_LABEL = "fastest flag time (s)"
NO_FINISHER_NOTE = "no agent reached the flag"
# Where in its panel the note is written, as a fraction of the panel's width and height: its centre.
NO_FINISHER_NOTE_POSITION = (0.5, 0.5)
SECONDS_PER_GENERATION_CHART_TITLE = "Seconds per generation"
SECONDS_AXIS_LABEL = "seconds (wall clock)"

# --- The comparison of several runs (spec section 13) -------------------------------------------------

# Made inside the runs folder, named after when the comparison was made: comparisons/YYYY-MM-DD_HH-MM/.
COMPARISONS_FOLDER_NAME = "comparisons"
COMPARISON_FOLDER_TIMESTAMP_FORMAT = "%Y-%m-%d_%H-%M"
FITNESS_COMPARISON_CHART_FILE_NAME = "fitness_comparison.png"
# The runs' summaries side by side: one column per run, headed by its run folder's name.
COMPARISON_FILE_NAME = "comparison.txt"
COMPARISON_RUN_HEADER = "Run"
COMPARISON_COLUMN_GAP = "   "
# Each run's colour is the next of the SERIES_COLOURS, never cycled, so at most this many runs are compared.
MAX_COMPARED_RUNS = len(SERIES_COLOURS)
FITNESS_COMPARISON_CHART_TITLE = "Best and mean fitness per generation"
# A run's line is labelled by its run folder's name: its run name, after when it started.
RUN_SERIES_LABEL_FORMAT = "{run} {series}"
