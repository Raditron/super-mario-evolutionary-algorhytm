"""Every tunable value of the coursework report's tooling: the title page, the page and text
styles of the .docx, the flowcharts' look and the screenshots' moments."""

from pathlib import Path

COURSEWORK_FOLDER = Path(__file__).resolve().parent
REPO_ROOT = COURSEWORK_FOLDER.parent.parent
FIGURES_FOLDER = COURSEWORK_FOLDER / "figures"
REPORT_SOURCE = COURSEWORK_FOLDER / "report.md"
REPORT_OUTPUT = COURSEWORK_FOLDER / "Курсов_проект_Русев_361223042.docx"

# Title page
UNIVERSITY_NAME = "Технически университет – София"
COURSE_NAME = "Представяне и моделиране на знания"
DOCUMENT_KIND = "КУРСОВ ПРОЕКТ"
TOPIC = ("Невроеволюция: обучение на агент за платформена игра "
         "чрез генетичен алгоритъм и невронна мрежа")
STUDENT_NAME = "Радослав Петров Русев"
FACULTY_NUMBER = "361223042"
STUDENT_GROUP = "21а"
HAND_IN_DATE = "04.11.2026"
CITY = "София"
LOGO_IMAGE = FIGURES_FOLDER / "tu_sofia_logo.png"
LOGO_HEIGHT_CM = 4.0

# The watermark: the blue logo, faded, centred on every page behind the text
WATERMARK_IMAGE = FIGURES_FOLDER / "tu_sofia_logo_blue.png"
WATERMARK_WIDTH_CM = 14.0
WATERMARK_OPACITY = 0.08  # 0 invisible, 1 the logo as it is

# The appendix: the algorithm package, then the run config and the game's one call site of it
APPENDIX_PACKAGE = REPO_ROOT / "neuroevolution"
APPENDIX_EXTRA_FILES = (REPO_ROOT / "config.toml", REPO_ROOT / "mario" / "modes" / "train_mode.py")

# Page and text (python-docx lengths are given in these units)
PAGE_WIDTH_CM = 21.0
PAGE_HEIGHT_CM = 29.7
PAGE_MARGIN_CM = 2.5
BODY_FONT = "Calibri"
BODY_FONT_SIZE_PT = 12
BODY_LINE_SPACING = 1.15
BODY_SPACE_AFTER_PT = 6
FIRST_LINE_INDENT_CM = 1.0
HEADING_FONT_SIZES_PT = {1: 16, 2: 14, 3: 12}
HEADING_SPACE_BEFORE_PT = {1: 18, 2: 12, 3: 10}
HEADING_SPACE_AFTER_PT = 6
CODE_FONT = "Consolas"
CODE_FONT_SIZE_PT = 8
INLINE_CODE_FONT_SIZE_PT = 11
CAPTION_FONT_SIZE_PT = 10
TABLE_FONT_SIZE_PT = 10
TABLE_HEADER_SHADING = "D9E2F3"
PLACEHOLDER_HIGHLIGHT = "YELLOW"
FIGURE_WIDTH_CM = 16.0
FIGURE_MAX_HEIGHT_CM = 21.5
TITLE_FONT_SIZE_PT = 22
TITLE_TOPIC_FONT_SIZE_PT = 16
TITLE_DETAILS_FONT_SIZE_PT = 13
TITLE_GAP_LINES = 3
FIGURE_CAPTION_PREFIX = "Фигура"
TABLE_CAPTION_PREFIX = "Таблица"
TABLE_OF_CONTENTS_HEADING = "Съдържание"
TABLE_OF_CONTENTS_LEVELS = "1-3"
# A table column is never given less than this weight (its longest cell's length), nor more
TABLE_COLUMN_MINIMUM_WEIGHT = 8
TABLE_COLUMN_MAXIMUM_WEIGHT = 60
LIST_INDENT_CM = 1.0
LIST_HANGING_CM = 0.5
REFERENCE_HANGING_CM = 1.0
FORMULA_FONT = "Cambria Math"
WORD_PDF_FORMAT = 17  # Word's wdExportFormatPDF

# Flowcharts (matplotlib, sizes in grid units of the chart's own axes)
FLOWCHART_FONT_FAMILY = ["Calibri", "DejaVu Sans"]
FLOWCHART_FONT_SIZE = 13
FLOWCHART_DPI = 200
FLOWCHART_INCHES_PER_UNIT = 0.62
FLOWCHART_LINE_WIDTH = 1.5
FLOWCHART_ARROW_HEAD_SIZE = 16
FLOWCHART_CHARACTER_WIDTH = 0.15  # roughly, one character of the font
FLOWCHART_LINE_HEIGHT = 0.39
FLOWCHART_TEXT_LINE_SPACING = 1.3
FLOWCHART_NODE_MINIMUM_WIDTH = 3.0
FLOWCHART_NODE_PADDING_X = 0.35
FLOWCHART_NODE_PADDING_Y = 0.18
FLOWCHART_TERMINAL_ROUNDING = 0.45
# A diamond's text fits when the diamond is this many times wider and taller than the text
FLOWCHART_DIAMOND_WIDTH_PER_TEXT_WIDTH = 1.56
FLOWCHART_DIAMOND_HEIGHT_PER_TEXT_HEIGHT = 1.78
FLOWCHART_PARALLELOGRAM_SLANT = 0.3
FLOWCHART_ROW_GAP = 0.42  # between a node and the next one below it
FLOWCHART_COLUMN_GAP = 0.9  # between columns, and from a column to a loop line beside it
FLOWCHART_BRANCH_MERGE_HEIGHT = 0.3  # how far above a node two branches meet before entering it
FLOWCHART_MARGIN = 0.6
FLOWCHART_EDGE_LABEL_OFFSET = 0.15
FLOWCHART_COLOURS = {
    "terminal": "#D5E8D4",
    "process": "#DAE8FC",
    "decision": "#FFF2CC",
    "data": "#F8CECC",
}
FLOWCHART_EDGE_COLOUR = "#333333"
FLOWCHART_BORDER_COLOUR = "#333333"

# Screenshots (taken off-screen from the real Viewer)
SCREENSHOT_RUN = REPO_ROOT / "runs" / "2026-11-04_12-01_first-run"
SCREENSHOT_SCALE = 3
BEST_AGENT_GENERATION = 200
BEST_AGENT_SHOT_TICK = 400
GHOST_SHOTS = ((1, 2.0), (200, 12.0))  # (generation, seconds into its all-ghost replay)
