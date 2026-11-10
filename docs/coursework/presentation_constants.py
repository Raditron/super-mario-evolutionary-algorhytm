"""Every tunable value of the coursework presentation: where its inputs live, the slide canvas,
the palette, the fonts, the pixel headlines and each slide's layout (all lengths in inches)."""

from pathlib import Path

COURSEWORK_FOLDER = Path(__file__).resolve().parent
REPO_ROOT = COURSEWORK_FOLDER.parent.parent
FIGURES_FOLDER = COURSEWORK_FOLDER / "figures"
SPRITES_FOLDER = REPO_ROOT / "assets" / "sprites"
PRESENTATION_OUTPUT = COURSEWORK_FOLDER / "Презентация_Русев_361223042.pptx"

# The training run whose results the deck shows (the screenshots' run shares its seed, so its
# first 200 generations are the same)
RESULTS_RUN = REPO_ROOT / "runs" / "2026-11-04_14-31_first-run"
TICKS_PER_SECOND = 60
FLAG_END_REASON = "reached_flag"
SECONDS_PER_HOUR = 3600

# Measured in the report's section 4 (another run was training alongside, so upper bounds)
MEASURED_NEXT_GENOMES_SECONDS = 0.28
MEASURED_EARLY_GENERATION = 1
MEASURED_EARLY_GENERATION_SECONDS = 6.7
MEASURED_LATE_GENERATION = 165
MEASURED_LATE_GENERATION_SECONDS = 29.8
# The slowest possible finisher (the level timer's full 9 600 ticks) still earns at least this
SLOWEST_FINISHER_FITNESS = 10_000
REPO_URL = "github.com/Raditron/super-mario-evolutionary-algorhytm"

# Canvas (16:9)
SLIDE_WIDTH = 13.333
SLIDE_HEIGHT = 7.5
MARGIN = 0.6
CONTENT_WIDTH = SLIDE_WIDTH - 2 * MARGIN
CONTENT_TOP = 2.0  # below a two-line headline
CONTENT_BOTTOM = 6.6  # above the footer
BLOCK_GAP = 0.3

# Palette: the observation grid's own colours (+1 green, -1 purple) and coin gold on night ink
INK = "0F1222"  # the background
SURFACE = "1B2036"  # cards and frames
SURFACE_EDGE = "2C3354"
LINE_DIM = "323A5E"  # the network's connections and other quiet lines
TEXT = "F3EFE6"
MUTED = "8C93AE"
GOLD = "FFC93C"  # fitness, coins, the one thing to look at
GREEN = "5DD39E"  # +1, a solid block
PURPLE = "B07CFF"  # -1, an enemy
SKY = "6FA8FF"  # a second data series

# Fonts: real text uses fonts every Windows Office has; the pixel font is drawn into pictures
BODY_FONT = "Segoe UI"
BODY_SEMIBOLD_FONT = "Segoe UI Semibold"
CODE_FONT = "Consolas"
PIXEL_FONT_FILE = COURSEWORK_FOLDER / "fonts" / "Handjet.ttf"  # SIL OFL, full Cyrillic
PIXEL_FONT_WEIGHT = b"Bold"
PIXEL_RENDER_DPI = 300
POINTS_PER_INCH = 72
PIXEL_LINE_SPACING = 1.0
PIXEL_HIGHLIGHT_MARK = "*"  # *words* between two marks are drawn in gold

# Type sizes (points)
HEADLINE_SIZE = 46
TITLE_SIZE = 80
BIG_NUMBER_SIZE = 72
MEDIUM_NUMBER_SIZE = 48
SUBTITLE_SIZE = 22
BODY_SIZE = 16
LABEL_SIZE = 14
CAPTION_SIZE = 12

# Headline and footer
HEADLINE_TOP = 0.65
HEADLINE_MAX_LINES = 1  # one takeaway sentence; a longer one gets shortened
FOOTER_TOP = 6.95
PROGRESS_SQUARE_SIZE = 0.11
PROGRESS_SQUARE_GAP = 0.06
PROGRESS_SQUARE_OUTLINE_WIDTH_PT = 0.75
SLIDE_NUMBER_WIDTH = 1.0

# Shapes
CARD_CORNER = 0.06  # a rounded rectangle's corner, as a share of its shorter side
FRAME_WIDTH_PT = 2.0
LINE_WIDTH_PT = 1.0
ARROW_WIDTH_PT = 2.0
PIXEL_SPRITE_SCALE = 8  # sprites are upscaled with nearest neighbour, never smoothed

# The observation grid, as drawn on the title and observation slides: 13 columns by 12 rows
# around the hero ('#' solid +1, 'e' enemy -1, '.' empty 0, 'h' the hero's own cell)
OBSERVATION_GRID_ROWS = (
    ".............",
    ".............",
    "..........##.",
    ".............",
    "......#.#.#..",
    "...h.........",
    ".............",
    ".....##......",
    ".....##......",
    "..e..##...e..",
    "#############",
    "#############",
)
GRID_CELL_PIXELS = 40
GRID_CELL_GAP_PIXELS = 4

# The genome picture: each gene a square, values scaled by their spread and clipped
GENOME_GENE_PIXELS = 6
GENOME_PART_GAP_GENES = 3
GENOME_CLIP_SPREADS = 2.5

# Slide 1: title
TITLE_LOGO_SIZE = 0.75
TITLE_TEXT_WIDTH = 6.9
TITLE_TOP = 1.85
TITLE_DETAILS_TOP = 6.1
TITLE_SUBTITLE_SIZE = 20
TITLE_GRID_LEFT = 7.9
TITLE_GRID_WIDTH = 4.8

# Slide 2: the goal
GOAL_SCREENSHOT_HEIGHT = 4.5
GOAL_STAT_HEIGHT = 1.45

# Slide 3: the idea
IDEA_CARD_HEIGHT = 3.9

# Slide 4: the observation
OBSERVATION_SCREENSHOT_HEIGHT = 4.6
OBSERVATION_LEGEND_SWATCH = 0.32
OBSERVATION_LEGEND_ITEM_WIDTHS = (2.45, 1.55, 1.6)  # each swatch with its label

# Slide 5: the network
NETWORK_INPUT_GRID_WIDTH = 2.6
NETWORK_HIDDEN_X = 6.4
NETWORK_HIDDEN_NODE_SIZE = 0.14
NETWORK_OUTPUT_X = 9.4
NETWORK_OUTPUT_WIDTH = 2.4
NETWORK_OUTPUT_HEIGHT = 0.5
NETWORK_TOP = 2.05
NETWORK_HEIGHT = 4.0

# Slide 6: the genome
GENOME_PICTURE_TOP = 2.2
GENOME_FACT_TOP = 5.1

# Slide 7: the generation cycle
CYCLE_CARD_TOP = 2.45
CYCLE_CARD_HEIGHT = 2.35
CYCLE_ARROW_GAP = 0.42
CYCLE_RETURN_Y = 5.55

# Slide 8: fitness
FITNESS_FORMULA_TOP = 2.05
FITNESS_CHART_TOP = 3.05
FITNESS_CHART_WIDTH = 8.0
FITNESS_BAR_GAP_PERCENT = 45
FITNESS_AXIS_HEADROOM = 1.18  # the longest bar leaves this much room for its label

# Slide 9: the boundary between the game and the algorithm
BOUNDARY_SIDE_WIDTH = 3.6
BOUNDARY_TOP = 2.15
BOUNDARY_HEIGHT = 3.35
BOUNDARY_METHOD_HEIGHT = 0.58

# Slide 10: where the time goes
TIME_BAR_HEIGHT = 0.55
TIME_BARS_TOP = 4.25
TIME_BAR_LEFT = 3.1
TIME_LEGEND_ITEM_WIDTH = 3.4

# Slide 11: the results chart (its plot area is placed by hand so labels can sit on it)
RESULTS_CHART_TOP = 1.95
RESULTS_CHART_HEIGHT = 4.75
RESULTS_PLOT_LEFT = 0.08  # shares of the chart's frame
RESULTS_PLOT_TOP = 0.05
RESULTS_PLOT_WIDTH = 0.8
RESULTS_PLOT_HEIGHT = 0.82
RESULTS_FITNESS_AXIS_MAXIMUM = 25_000
RESULTS_FITNESS_AXIS_STEP = 5_000
RESULTS_GENERATION_AXIS_STEP = 100
RESULTS_BEST_LINE_WIDTH_PT = 2.75
RESULTS_AVERAGE_LINE_WIDTH_PT = 2.0
RESULTS_MARKER_LINE_WIDTH_PT = 1.5
RESULTS_GRID_LINE_WIDTH_PT = 0.5
# Thousands apart by a space whatever the viewer's locale; below 1 000 just the number
RESULTS_AXIS_NUMBER_FORMAT = "[>=1000]# ##0;0"

# Slide 12: chaos to purpose
REPLAY_SCREENSHOT_WIDTH = 3.75
REPLAY_GENERATIONS = ((1, 2), (200, 12))  # (generation, seconds into its replay), as captured

# Slide 13: strengths and weaknesses
VERDICT_CARD_HEIGHT = 4.3

# Slide 14: thanks
THANKS_TILE_SIZE = 0.8  # one sprite tile, on the closing slide
THANKS_TITLE_TOP = 1.9
THANKS_HERO_LEFT = 1.3
THANKS_ENEMY_RIGHT = 3.0  # from the right edge
