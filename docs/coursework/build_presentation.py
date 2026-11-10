"""Builds the coursework presentation (.pptx): fourteen slides, each one message with one picture or
number, and the narration in the speaker notes. The results are read fresh from a recorded run.

py docs/coursework/build_presentation.py
"""

import io
from collections.abc import Callable

from PIL import Image
from pptx import Presentation
from pptx.chart.data import CategoryChartData, XyChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION, XL_TICK_LABEL_POSITION, XL_TICK_MARK
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt
from lxml import etree

from presentation_canvas import (
    NO_BREAK_SPACE, PixelTextRenderer, Run, SlideCanvas, genome_picture, light_logo_picture,
    observation_grid_picture, png_bytes, sprite_picture,
)
from presentation_constants import (
    ARROW_WIDTH_PT, BIG_NUMBER_SIZE, BLOCK_GAP, BODY_FONT, BODY_SEMIBOLD_FONT, BODY_SIZE, BOUNDARY_HEIGHT,
    BOUNDARY_METHOD_HEIGHT, BOUNDARY_SIDE_WIDTH, BOUNDARY_TOP, CAPTION_SIZE, CODE_FONT, CONTENT_BOTTOM, CONTENT_TOP,
    CONTENT_WIDTH, CYCLE_ARROW_GAP, CYCLE_CARD_HEIGHT, CYCLE_CARD_TOP, CYCLE_RETURN_Y, FIGURES_FOLDER,
    FITNESS_AXIS_HEADROOM, FITNESS_BAR_GAP_PERCENT, FITNESS_CHART_TOP, FITNESS_CHART_WIDTH, FITNESS_FORMULA_TOP,
    FOOTER_TOP, FRAME_WIDTH_PT, GENOME_FACT_TOP, GENOME_PICTURE_TOP, GOAL_SCREENSHOT_HEIGHT, GOAL_STAT_HEIGHT, GOLD,
    GREEN, GRID_CELL_GAP_PIXELS, GRID_CELL_PIXELS, HEADLINE_MAX_LINES, HEADLINE_SIZE, HEADLINE_TOP,
    IDEA_CARD_HEIGHT, INK, LABEL_SIZE, LINE_DIM, LINE_WIDTH_PT, MARGIN, MEASURED_EARLY_GENERATION,
    MEASURED_EARLY_GENERATION_SECONDS, MEASURED_LATE_GENERATION, MEASURED_LATE_GENERATION_SECONDS,
    MEASURED_NEXT_GENOMES_SECONDS, MEDIUM_NUMBER_SIZE, MUTED, NETWORK_HEIGHT, NETWORK_HIDDEN_NODE_SIZE,
    NETWORK_HIDDEN_X, NETWORK_INPUT_GRID_WIDTH, NETWORK_OUTPUT_HEIGHT, NETWORK_OUTPUT_WIDTH, NETWORK_OUTPUT_X,
    NETWORK_TOP, OBSERVATION_GRID_ROWS, OBSERVATION_LEGEND_ITEM_WIDTHS, OBSERVATION_LEGEND_SWATCH,
    OBSERVATION_SCREENSHOT_HEIGHT, PIXEL_SPRITE_SCALE, POINTS_PER_INCH, PRESENTATION_OUTPUT, PROGRESS_SQUARE_GAP,
    PROGRESS_SQUARE_OUTLINE_WIDTH_PT, PROGRESS_SQUARE_SIZE, PURPLE, REPLAY_GENERATIONS, REPLAY_SCREENSHOT_WIDTH,
    REPO_URL, RESULTS_AVERAGE_LINE_WIDTH_PT, RESULTS_AXIS_NUMBER_FORMAT, RESULTS_BEST_LINE_WIDTH_PT,
    RESULTS_CHART_HEIGHT, RESULTS_CHART_TOP, RESULTS_FITNESS_AXIS_MAXIMUM, RESULTS_FITNESS_AXIS_STEP,
    RESULTS_GENERATION_AXIS_STEP, RESULTS_GRID_LINE_WIDTH_PT, RESULTS_MARKER_LINE_WIDTH_PT, RESULTS_PLOT_HEIGHT,
    RESULTS_PLOT_LEFT, RESULTS_PLOT_TOP, RESULTS_PLOT_WIDTH, RESULTS_RUN, SKY, SLIDE_HEIGHT, SLIDE_NUMBER_WIDTH,
    SLIDE_WIDTH, SLOWEST_FINISHER_FITNESS, SPRITES_FOLDER, SUBTITLE_SIZE, SURFACE, SURFACE_EDGE, TEXT,
    THANKS_ENEMY_RIGHT, THANKS_HERO_LEFT, THANKS_TILE_SIZE, THANKS_TITLE_TOP, TICKS_PER_SECOND, TIME_BARS_TOP,
    TIME_BAR_HEIGHT, TIME_BAR_LEFT, TIME_LEGEND_ITEM_WIDTH, TITLE_DETAILS_TOP, TITLE_GRID_LEFT, TITLE_GRID_WIDTH,
    TITLE_LOGO_SIZE, TITLE_SIZE, TITLE_SUBTITLE_SIZE, TITLE_TEXT_WIDTH, TITLE_TOP, VERDICT_CARD_HEIGHT,
)
from presentation_notes import SPEAKER_NOTES
from presentation_run_facts import RunFacts, read_run_facts
from report_constants import (
    COURSE_NAME, FACULTY_NUMBER, HAND_IN_DATE, LOGO_IMAGE, STUDENT_GROUP, STUDENT_NAME, UNIVERSITY_NAME,
)

# What the game hands the algorithm: the observation and the buttons
GRID_CELLS = 156
MOTION_NUMBERS = 4
INPUT_SIZE = GRID_CELLS + MOTION_NUMBERS
BUTTONS = ("← наляво", "→ надясно", "↓ надолу", "скок", "бягане")
OUTPUT_SIZE = len(BUTTONS)
PERCENT = 100
BYTES_PER_KILOBYTE = 1000
HERO_SPRITE = SPRITES_FOLDER / "mario_small.png"
HERO_JUMP_SPRITE = SPRITES_FOLDER / "mario_small_jump.png"
GROUND_SPRITE = SPRITES_FOLDER / "ground.png"
QUESTION_BLOCK_SPRITE = SPRITES_FOLDER / "question_block.png"
ENEMY_SPRITE = SPRITES_FOLDER / "goomba.png"


def bulgarian_number(value: float, decimals: int = 0) -> str:
    """3989 -> '3 989', 22.57 -> '22,57': a no-break space between thousands, a decimal comma."""
    return f"{value:,.{decimals}f}".replace(",", NO_BREAK_SPACE).replace(".", ",")


class DeckBuilder:
    """Adds the slides one by one, each with its headline, footer and speaker notes."""

    def __init__(self, facts: RunFacts):
        self.facts = facts
        self.presentation = Presentation()
        self.presentation.slide_width = Inches(SLIDE_WIDTH)
        self.presentation.slide_height = Inches(SLIDE_HEIGHT)
        self._blank_layout = self.presentation.slide_layouts[6]
        self._pixel_text = PixelTextRenderer()
        self._note_fields = self._speaker_note_fields()

    def build(self, slides: list[tuple[str, Callable[["DeckBuilder", SlideCanvas], None]]]) -> None:
        for number, (notes_key, draw) in enumerate(slides, start=1):
            canvas = SlideCanvas(self.presentation.slides.add_slide(self._blank_layout), self._pixel_text)
            canvas.fill_background()
            draw(self, canvas)
            if 1 < number < len(slides):
                self._footer(canvas, number, len(slides))
            canvas.notes(SPEAKER_NOTES[notes_key].format(**self._note_fields))

    def headline(self, canvas: SlideCanvas, marked_text: str) -> None:
        rendered = canvas.pixel_text(marked_text, MARGIN, HEADLINE_TOP, HEADLINE_SIZE, max_width=CONTENT_WIDTH)
        if rendered.line_count > HEADLINE_MAX_LINES:
            raise ValueError(f"headline runs to {rendered.line_count} lines: {marked_text!r}")

    @staticmethod
    def _footer(canvas: SlideCanvas, number: int, total: int) -> None:
        """A row of pixel squares, one per slide, filled up to this one; and the slide number."""
        square_y = FOOTER_TOP + (CAPTION_SIZE / POINTS_PER_INCH - PROGRESS_SQUARE_SIZE) / 2
        for index in range(total):
            x = MARGIN + index * (PROGRESS_SQUARE_SIZE + PROGRESS_SQUARE_GAP)
            reached = index < number
            canvas.card(x, square_y, PROGRESS_SQUARE_SIZE, PROGRESS_SQUARE_SIZE, fill=GOLD if reached else None,
                        outline=None if reached else SURFACE_EDGE,
                        outline_width_pt=PROGRESS_SQUARE_OUTLINE_WIDTH_PT, rounded=False)
        canvas.text(SLIDE_WIDTH - MARGIN - SLIDE_NUMBER_WIDTH, FOOTER_TOP, SLIDE_NUMBER_WIDTH, CAPTION_SIZE / POINTS_PER_INCH * 1.5,
                    f"{number} / {total}", CAPTION_SIZE, MUTED, align=PP_ALIGN.RIGHT)

    def _speaker_note_fields(self) -> dict:
        facts, settings = self.facts, self.facts.settings
        return {
            "population": bulgarian_number(settings["population_size"]),
            "seed": settings["seed"],
            "last_generation": facts.last_generation,
            "ticks_per_second": TICKS_PER_SECOND,
            "hidden": settings["hidden_layer_size"],
            "elite_count": settings["elite_count"],
            "elite_percent": bulgarian_number(PERCENT * settings["elite_count"] / settings["population_size"]),
            "tournament_size": settings["tournament_size"],
            "crossover_percent": bulgarian_number(PERCENT * settings["crossover_rate"]),
            "mutation_percent": bulgarian_number(PERCENT * settings["mutation_rate"]),
            "mutation_strength": bulgarian_number(settings["mutation_strength"], 2),
            "mutated_genes": bulgarian_number(settings["mutation_rate"] * facts.genome_size),
            "coin_reward": settings["coin_reward"],
            "flag_reward": bulgarian_number(settings["flag_reward"]),
            "time_reward": bulgarian_number(settings["time_reward"], 2),
            "slowest_finisher": bulgarian_number(SLOWEST_FINISHER_FITNESS),
            "best_without_flag": bulgarian_number(facts.best_fitness_without_flag),
            "next_genomes_seconds": bulgarian_number(MEASURED_NEXT_GENOMES_SECONDS, 2),
            "early_seconds": bulgarian_number(MEASURED_EARLY_GENERATION_SECONDS, 1),
            "late_seconds": bulgarian_number(MEASURED_LATE_GENERATION_SECONDS, 1),
            "first_flag": facts.first_flag_generation,
            "generations_before_flag": facts.first_flag_generation - 1,
            "total_hours": bulgarian_number(facts.total_hours, 1),
            "last_finishers": facts.last_finishers,
            "fastest_finish": bulgarian_number(facts.fastest_finish_seconds, 1),
        }


# The slides, in order ---------------------------------------------------------------------------------

def title_slide(deck: DeckBuilder, canvas: SlideCanvas) -> None:
    canvas.picture(light_logo_picture(LOGO_IMAGE), MARGIN, MARGIN, height=TITLE_LOGO_SIZE, alt_text=UNIVERSITY_NAME)
    text_left = MARGIN + TITLE_LOGO_SIZE + BLOCK_GAP
    canvas.text(text_left, MARGIN, TITLE_TEXT_WIDTH, TITLE_LOGO_SIZE,
                [UNIVERSITY_NAME, COURSE_NAME], LABEL_SIZE, MUTED, anchor=MSO_ANCHOR.MIDDLE)

    title = canvas.pixel_text("Невро-\nеволюция", MARGIN, TITLE_TOP, TITLE_SIZE, GOLD)
    subtitle_top = TITLE_TOP + title.height + 2 * BLOCK_GAP
    canvas.text(MARGIN, subtitle_top, TITLE_TEXT_WIDTH, TITLE_DETAILS_TOP - subtitle_top - BLOCK_GAP,
                "Агент, който сам се научава да минава ниво от платформена игра – "
                "с генетичен алгоритъм и невронна мрежа", TITLE_SUBTITLE_SIZE, TEXT, line_spacing=1.1)

    canvas.text(MARGIN, TITLE_DETAILS_TOP, TITLE_TEXT_WIDTH, 0.9,
                [[Run(STUDENT_NAME, TEXT, BODY_SEMIBOLD_FONT)],
                 f"ф. № {FACULTY_NUMBER} · група {STUDENT_GROUP} · {HAND_IN_DATE}"], BODY_SIZE, MUTED,
                space_after_pt=2)

    grid_height = TITLE_GRID_WIDTH * _grid_aspect()
    canvas.picture(observation_grid_picture(HERO_SPRITE), TITLE_GRID_LEFT, (SLIDE_HEIGHT - grid_height) / 2,
                   width=TITLE_GRID_WIDTH,
                   alt_text="Решетката на наблюдението: 13 × 12 клетки около героя")


def goal_slide(deck: DeckBuilder, canvas: SlideCanvas) -> None:
    deck.headline(canvas, "Целта: да мине ниво 1-1, *без да му се показва как*")
    stats = (
        (bulgarian_number(deck.facts.settings["population_size"]), "агента играят нивото във всяко поколение"),
        (str(TICKS_PER_SECOND), "решения в секунда – кои от 5-те бутона да натисне"),
        ("0", "демонстрации как се играе"),
    )
    for index, (number, label) in enumerate(stats):
        _stat(canvas, MARGIN, CONTENT_TOP + 0.1 + index * GOAL_STAT_HEIGHT, number, label, 6.4)
    screenshot_width = GOAL_SCREENSHOT_HEIGHT * _screenshot_aspect()
    _framed_picture(canvas, FIGURES_FOLDER / "screenshot_sprite_view.png", SLIDE_WIDTH - MARGIN - screenshot_width,
                    CONTENT_TOP, screenshot_width, GOAL_SCREENSHOT_HEIGHT,
                    "Нивото в изгледа със спрайтове: най-добрият агент от поколение 200 във въздуха")


def idea_slide(deck: DeckBuilder, canvas: SlideCanvas) -> None:
    deck.headline(canvas, "Еволюцията иска от всеки опит само *едно число*")
    card_width = (CONTENT_WIDTH - BLOCK_GAP) / 2
    cards = (
        ("ОБУЧЕНИЕ С УЧИТЕЛ", "?", MUTED, None,
         "Иска верния бутон за всеки тик. В играта такъв отговор няма – дали един скок е бил добър, "
         "личи чак секунди по-късно."),
        ("НЕВРОЕВОЛЮЦИЯ", bulgarian_number(deck.facts.best_fitness_overall), GOLD, GOLD,
         "Иска само годността на целия опит – едно число на агент. Най-годните предават теглата си "
         "на следващото поколение."),
    )
    for index, (label, big, colour, outline, body) in enumerate(cards):
        x = MARGIN + index * (card_width + BLOCK_GAP)
        top = CONTENT_TOP + 0.2
        canvas.card(x, top, card_width, IDEA_CARD_HEIGHT, outline=outline, outline_width_pt=FRAME_WIDTH_PT)
        inner = x + 0.45
        canvas.text(inner, top + 0.4, card_width - 0.9, 0.3, label, LABEL_SIZE, colour, BODY_SEMIBOLD_FONT)
        canvas.pixel_text(big, inner, top + 0.85, BIG_NUMBER_SIZE, colour)
        canvas.text(inner, top + 2.2, card_width - 0.9, 1.4, body, BODY_SIZE, TEXT if outline else MUTED,
                    line_spacing=1.1)


def observation_slide(deck: DeckBuilder, canvas: SlideCanvas) -> None:
    deck.headline(canvas, "На всеки тик агентът вижда *160 числа*")
    screenshot_width = OBSERVATION_SCREENSHOT_HEIGHT * _screenshot_aspect()
    _framed_picture(canvas, FIGURES_FOLDER / "screenshot_debug_view.png", MARGIN, CONTENT_TOP, screenshot_width,
                    OBSERVATION_SCREENSHOT_HEIGHT,
                    "Диагностичният изглед: решетката на наблюдението върху нивото и четирите числа за движението")
    right = MARGIN + screenshot_width + 0.7
    right_width = SLIDE_WIDTH - MARGIN - right
    canvas.pixel_text(f"{GRID_CELLS} + {MOTION_NUMBERS} = *{INPUT_SIZE}*", right, CONTENT_TOP, BIG_NUMBER_SIZE)
    parts = ((str(GRID_CELLS), "клетки от решетка 13 × 12 около героя: 3 колони назад и 9 напред"),
             (str(MOTION_NUMBERS), "числа за движението: двете скорости, височината и дали стои на земята"))
    for index, (number, label) in enumerate(parts):
        top = CONTENT_TOP + 1.25 + index * 0.85
        canvas.pixel_text(number, right, top, MEDIUM_NUMBER_SIZE * 0.75, GOLD)
        canvas.text(right + 0.95, top + 0.02, right_width - 0.95, 0.75, label, BODY_SIZE, TEXT, line_spacing=1.05)
    legend = ((GREEN, None, "+1", "твърд блок"), (PURPLE, None, "−1", "враг"), (SURFACE, SURFACE_EDGE, "0", "празно"))
    legend_top = CONTENT_TOP + 3.35
    x = right
    for (fill, outline, value, label), item_width in zip(legend, OBSERVATION_LEGEND_ITEM_WIDTHS):
        canvas.card(x, legend_top, OBSERVATION_LEGEND_SWATCH, OBSERVATION_LEGEND_SWATCH, fill=fill, outline=outline,
                    rounded=False)
        canvas.text(x + OBSERVATION_LEGEND_SWATCH + 0.15, legend_top - 0.03, 1.6, 0.4,
                    [[Run(value + " ", TEXT, BODY_SEMIBOLD_FONT), Run(label)]], BODY_SIZE, MUTED)
        x += item_width


def network_slide(deck: DeckBuilder, canvas: SlideCanvas) -> None:
    hidden_size = deck.facts.settings["hidden_layer_size"]
    deck.headline(canvas, f"Мозъкът: от *{INPUT_SIZE} числа* до *5 бутона* през {hidden_size} неврона")
    grid_width = NETWORK_INPUT_GRID_WIDTH
    grid_height = grid_width * _grid_aspect()
    grid_left = MARGIN + 0.3
    grid_top = NETWORK_TOP + (NETWORK_HEIGHT - grid_height) / 2
    hidden_step = NETWORK_HEIGHT / (hidden_size - 1)
    hidden_centres = [NETWORK_TOP + index * hidden_step for index in range(hidden_size)]
    output_step = NETWORK_HEIGHT / len(BUTTONS)
    output_centres = [NETWORK_TOP + (index + 0.5) * output_step for index in range(len(BUTTONS))]
    node_radius = NETWORK_HIDDEN_NODE_SIZE / 2

    for index, centre in enumerate(hidden_centres):
        canvas.line(grid_left + grid_width, grid_top + grid_height * index / (hidden_size - 1),
                    NETWORK_HIDDEN_X, centre, LINE_DIM, LINE_WIDTH_PT * 0.75)
        for output_centre in output_centres:
            canvas.line(NETWORK_HIDDEN_X + node_radius, centre, NETWORK_OUTPUT_X, output_centre, LINE_DIM,
                        LINE_WIDTH_PT * 0.5)
    canvas.picture(observation_grid_picture(HERO_SPRITE), grid_left, grid_top, width=grid_width,
                   alt_text="Входът: решетката на наблюдението")
    for centre in hidden_centres:
        canvas.dot(NETWORK_HIDDEN_X - node_radius, centre - node_radius, NETWORK_HIDDEN_NODE_SIZE, TEXT)
    for button, centre in zip(BUTTONS, output_centres):
        top = centre - NETWORK_OUTPUT_HEIGHT / 2
        canvas.card(NETWORK_OUTPUT_X, top, NETWORK_OUTPUT_WIDTH, NETWORK_OUTPUT_HEIGHT, outline=GOLD,
                    outline_width_pt=FRAME_WIDTH_PT / 2)
        canvas.text(NETWORK_OUTPUT_X + 0.25, top, NETWORK_OUTPUT_WIDTH - 0.5, NETWORK_OUTPUT_HEIGHT, button,
                    BODY_SIZE, TEXT, BODY_SEMIBOLD_FONT, anchor=MSO_ANCHOR.MIDDLE)

    label_top = NETWORK_TOP + NETWORK_HEIGHT + 0.25
    labels = ((grid_left + grid_width / 2, f"{INPUT_SIZE} входа: {GRID_CELLS} клетки + {MOTION_NUMBERS} числа"),
              (NETWORK_HIDDEN_X, f"{hidden_size} скрити неврона, tanh"),
              (NETWORK_OUTPUT_X + NETWORK_OUTPUT_WIDTH / 2, "натиснат, ако изходът > 0"))
    for centre, label in labels:
        canvas.text(centre - 1.7, label_top, 3.4, 0.35, label, LABEL_SIZE, MUTED, align=PP_ALIGN.CENTER)


def genome_slide(deck: DeckBuilder, canvas: SlideCanvas) -> None:
    deck.headline(canvas, f"Целият мозък е *{bulgarian_number(deck.facts.genome_size)} гена* – един масив от числа")
    hidden_size = deck.facts.settings["hidden_layer_size"]
    output_size = OUTPUT_SIZE
    genome = deck.facts.last_best_genome
    sizes = (INPUT_SIZE * hidden_size, hidden_size, hidden_size * output_size, output_size)
    boundaries = [sum(sizes[:index]) for index in range(len(sizes) + 1)]
    first_weights, first_biases, second_weights, second_biases = (
        genome[start:end] for start, end in zip(boundaries, boundaries[1:]))
    picture, spans = genome_picture([
        first_weights.reshape(INPUT_SIZE, hidden_size).T,
        first_biases.reshape(hidden_size, 1),
        second_weights.reshape(hidden_size, output_size),
        second_biases.reshape(output_size, 1),
    ])
    shown = canvas.picture(picture, MARGIN, GENOME_PICTURE_TOP, width=CONTENT_WIDTH,
                           alt_text=f"Геномът на най-добрия агент от поколение {deck.facts.last_generation}: "
                                    "зелено положителни, лилаво отрицателни тегла")
    label_top = GENOME_PICTURE_TOP + shown.height.inches + 0.15
    canvas.text(MARGIN, label_top, 6.5, 0.35,
                [[Run("W₁ ", TEXT, BODY_SEMIBOLD_FONT),
                  Run(f"{INPUT_SIZE} × {hidden_size} = {bulgarian_number(sizes[0])} тегла на скрития слой")]],
                LABEL_SIZE, MUTED)
    small_parts_left = MARGIN + CONTENT_WIDTH * spans[1][0]
    canvas.text(small_parts_left - 4.5, label_top, 4.5 + CONTENT_WIDTH * (1 - spans[1][0]), 0.35,
                [[Run("b₁ ", TEXT, BODY_SEMIBOLD_FONT), Run(f"{hidden_size}   "),
                  Run("W₂ ", TEXT, BODY_SEMIBOLD_FONT), Run(f"{hidden_size} × {output_size} = {sizes[2]}   "),
                  Run("b₂ ", TEXT, BODY_SEMIBOLD_FONT), Run(str(output_size))]],
                LABEL_SIZE, MUTED, align=PP_ALIGN.RIGHT)

    facts = (("1 ген = 1 тегло", "директно кодиране: W₁, b₁, W₂, b₂ едно след друго"),
             ("ЛеКун", "начални тегла N(0; 1/√n) – сумите не насищат tanh"),
             (f"{round(genome.nbytes / BYTES_PER_KILOBYTE)} KB",
              f"на агент: {bulgarian_number(genome.size)} числа × {genome.itemsize} байта"))
    card_width = (CONTENT_WIDTH - 2 * BLOCK_GAP) / len(facts)
    for index, (big, label) in enumerate(facts):
        x = MARGIN + index * (card_width + BLOCK_GAP)
        canvas.card(x, GENOME_FACT_TOP, card_width, 1.35)
        canvas.pixel_text(big, x + 0.3, GENOME_FACT_TOP + 0.22, MEDIUM_NUMBER_SIZE * 0.75, GOLD)
        canvas.text(x + 0.3, GENOME_FACT_TOP + 0.75, card_width - 0.6, 0.5, label, LABEL_SIZE, MUTED)


def cycle_slide(deck: DeckBuilder, canvas: SlideCanvas) -> None:
    settings = deck.facts.settings
    deck.headline(canvas, "Новото поколение се ражда от *най-годните*")
    steps = (
        (bulgarian_number(settings["population_size"]), "Оценка", "всеки агент изиграва нивото веднъж"),
        (str(settings["elite_count"]), "Елити", "най-добрите минават без промяна"),
        (f"k = {settings['tournament_size']}", "Турнир", "от трима случайни печели най-годният"),
        (f"{bulgarian_number(PERCENT * settings['crossover_rate'])}%", "Кръстосване",
         "всеки ген идва от единия или другия родител"),
        (f"{bulgarian_number(PERCENT * settings['mutation_rate'])}%", "Мутация",
         f"гаусова добавка, σ = {bulgarian_number(settings['mutation_strength'], 2)}"),
    )
    card_width = (CONTENT_WIDTH - CYCLE_ARROW_GAP * (len(steps) - 1)) / len(steps)
    card_centres = []
    for index, (value, name, description) in enumerate(steps):
        x = MARGIN + index * (card_width + CYCLE_ARROW_GAP)
        card_centres.append(x + card_width / 2)
        canvas.card(x, CYCLE_CARD_TOP, card_width, CYCLE_CARD_HEIGHT)
        canvas.pixel_text(value, x + 0.25, CYCLE_CARD_TOP + 0.3, MEDIUM_NUMBER_SIZE, GOLD)
        canvas.text(x + 0.25, CYCLE_CARD_TOP + 1.0, card_width - 0.5, 0.35, name, BODY_SIZE + 2, TEXT,
                    BODY_SEMIBOLD_FONT)
        canvas.text(x + 0.25, CYCLE_CARD_TOP + 1.45, card_width - 0.5, 0.8, description, LABEL_SIZE, MUTED,
                    line_spacing=1.05)
        if index:
            arrow_y = CYCLE_CARD_TOP + CYCLE_CARD_HEIGHT / 2
            canvas.line(x - CYCLE_ARROW_GAP + 0.07, arrow_y, x - 0.07, arrow_y, GOLD, ARROW_WIDTH_PT, arrow=True)
    card_bottom = CYCLE_CARD_TOP + CYCLE_CARD_HEIGHT
    canvas.line(card_centres[-1], card_bottom, card_centres[-1], CYCLE_RETURN_Y, MUTED, ARROW_WIDTH_PT)
    canvas.line(card_centres[-1], CYCLE_RETURN_Y, card_centres[0], CYCLE_RETURN_Y, MUTED, ARROW_WIDTH_PT)
    canvas.line(card_centres[0], CYCLE_RETURN_Y, card_centres[0], card_bottom + 0.05, MUTED, ARROW_WIDTH_PT,
                arrow=True)
    canvas.text(MARGIN, CYCLE_RETURN_Y + 0.15, CONTENT_WIDTH, 0.4,
                [[Run("отново и отново – ", MUTED), Run(f"{deck.facts.last_generation} поколения", TEXT,
                                                         BODY_SEMIBOLD_FONT)]],
                BODY_SIZE, align=PP_ALIGN.CENTER)


def fitness_slide(deck: DeckBuilder, canvas: SlideCanvas) -> None:
    settings = deck.facts.settings
    deck.headline(canvas, "Годност: достигането на флага *винаги печели*")
    canvas.text(MARGIN, FITNESS_FORMULA_TOP, CONTENT_WIDTH, 0.5,
                [[Run("годност = разстояние + "), Run(f"{settings['coin_reward']} · монети", TEXT),
                  Run(" + "),
                  Run(f"[флаг] · ({bulgarian_number(settings['flag_reward'])} − "
                      f"{bulgarian_number(settings['time_reward'], 2)} · тикове)", GOLD)]],
                SUBTITLE_SIZE, TEXT, BODY_SEMIBOLD_FONT)

    bars = (("Най-добрият без флаг", deck.facts.best_fitness_without_flag, MUTED),
            ("Най-бавният възможен с флаг", SLOWEST_FINISHER_FITNESS, GOLD),
            ("Най-добрият с флаг", deck.facts.best_fitness_overall, GOLD))
    chart_data = CategoryChartData()
    chart_data.categories = [label for label, _, _ in bars]
    chart_data.add_series("годност", [value for _, value, _ in bars])
    chart_height = CONTENT_BOTTOM - FITNESS_CHART_TOP
    chart = canvas.slide.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(MARGIN), Inches(FITNESS_CHART_TOP),
                                          Inches(FITNESS_CHART_WIDTH), Inches(chart_height), chart_data).chart
    _quiet_chart(chart)
    chart.plots[0].gap_width = FITNESS_BAR_GAP_PERCENT
    chart.value_axis.visible = False
    chart.value_axis.has_major_gridlines = False
    chart.value_axis.minimum_scale = 0
    chart.value_axis.maximum_scale = max(value for _, value, _ in bars) * FITNESS_AXIS_HEADROOM
    category_axis = chart.category_axis
    category_axis.reverse_order = True
    category_axis.format.line.fill.background()
    category_axis.major_tick_mark = XL_TICK_MARK.NONE
    _axis_labels(category_axis, TEXT, LABEL_SIZE)
    for point, (_, value, colour) in zip(chart.plots[0].series[0].points, bars):
        point.format.fill.solid()
        point.format.fill.fore_color.rgb = RGBColor.from_string(colour)
        label = point.data_label
        label.position = XL_LABEL_POSITION.OUTSIDE_END
        label.text_frame.text = bulgarian_number(value)
        font = label.text_frame.paragraphs[0].runs[0].font
        font.size, font.name, font.color.rgb = Pt(BODY_SIZE), BODY_SEMIBOLD_FONT, RGBColor.from_string(TEXT)

    trap_left = MARGIN + FITNESS_CHART_WIDTH + BLOCK_GAP + 0.1
    trap_width = SLIDE_WIDTH - MARGIN - trap_left
    canvas.card(trap_left, FITNESS_CHART_TOP + 0.1, trap_width, chart_height - 0.2)
    canvas.text(trap_left + 0.35, FITNESS_CHART_TOP + 0.45, trap_width - 0.7, 0.3, "КАПАН", LABEL_SIZE, PURPLE,
                BODY_SEMIBOLD_FONT)
    canvas.text(trap_left + 0.35, FITNESS_CHART_TOP + 0.85, trap_width - 0.7, chart_height - 1.2,
                ["Ако „по-бързо = по-добре“ важеше за всички, агент, загинал след 2 s, би бил „по\u2011добър“ "
                 "от внимателния.", "Затова времето се брои само за финиширалите."],
                BODY_SIZE, TEXT, space_after_pt=10, line_spacing=1.1)


def boundary_slide(deck: DeckBuilder, canvas: SlideCanvas) -> None:
    deck.headline(canvas, "Играта и алгоритъмът се срещат само в *4 метода*")
    sides = (
        (MARGIN, "Играта", ["реплика на ниво 1-1", "два изгледа, обучение на живо, повторения", "8 процеса"],
         "изградена с помощта на ИИ"),
        (SLIDE_WIDTH - MARGIN - BOUNDARY_SIDE_WIDTH, "Алгоритъмът",
         ["мрежа, генетичен алгоритъм, годност", "15 файла, ~465 реда", "само NumPy"], "написан от автора"),
    )
    for x, title, lines, author in sides:
        canvas.card(x, BOUNDARY_TOP, BOUNDARY_SIDE_WIDTH, BOUNDARY_HEIGHT)
        canvas.pixel_text(title, x + 0.35, BOUNDARY_TOP + 0.35, MEDIUM_NUMBER_SIZE * 0.8, GOLD)
        canvas.text(x + 0.35, BOUNDARY_TOP + 1.05, BOUNDARY_SIDE_WIDTH - 0.7, 1.6, lines, BODY_SIZE, TEXT,
                    space_after_pt=6)
        canvas.text(x + 0.35, BOUNDARY_TOP + BOUNDARY_HEIGHT - 0.6, BOUNDARY_SIDE_WIDTH - 0.7, 0.3, author,
                    LABEL_SIZE, MUTED)

    methods = ("initial_genomes", "build_brain", "fitness", "next_genomes")
    middle_left = MARGIN + BOUNDARY_SIDE_WIDTH
    middle_right = SLIDE_WIDTH - MARGIN - BOUNDARY_SIDE_WIDTH
    chip_width = middle_right - middle_left - 2 * 0.55
    chip_gap = (BOUNDARY_HEIGHT - len(methods) * BOUNDARY_METHOD_HEIGHT) / (len(methods) + 1)
    for index, method in enumerate(methods):
        top = BOUNDARY_TOP + chip_gap + index * (BOUNDARY_METHOD_HEIGHT + chip_gap)
        centre_y = top + BOUNDARY_METHOD_HEIGHT / 2
        canvas.line(middle_left, centre_y, middle_left + 0.55, centre_y, SURFACE_EDGE, FRAME_WIDTH_PT)
        canvas.line(middle_right - 0.55, centre_y, middle_right, centre_y, SURFACE_EDGE, FRAME_WIDTH_PT)
        canvas.card(middle_left + 0.55, top, chip_width, BOUNDARY_METHOD_HEIGHT, fill=INK, outline=GOLD,
                    outline_width_pt=FRAME_WIDTH_PT / 2)
        canvas.text(middle_left + 0.55, top, chip_width, BOUNDARY_METHOD_HEIGHT, method + "()", BODY_SIZE, TEXT,
                    CODE_FONT, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    canvas.text(MARGIN, BOUNDARY_TOP + BOUNDARY_HEIGHT + 0.4, CONTENT_WIDTH, 0.4,
                [[Run("134 автоматични теста", TEXT, BODY_SEMIBOLD_FONT), Run(" минават за 1–2 s · "),
                  Run("едно семе", TEXT, BODY_SEMIBOLD_FONT), Run(" прави всяко обучение възпроизводимо")]],
                BODY_SIZE, MUTED, align=PP_ALIGN.CENTER)


def time_slide(deck: DeckBuilder, canvas: SlideCanvas) -> None:
    deck.headline(canvas, "Генетичният алгоритъм е само *1–4 %* от времето")
    population = bulgarian_number(deck.facts.settings["population_size"])
    hidden_size = deck.facts.settings["hidden_layer_size"]
    big_numbers = ((MARGIN, f"{bulgarian_number(MEASURED_NEXT_GENOMES_SECONDS, 2)} s",
                    f"за ново поколение от {population} генома"),
                   (MARGIN + 6.3, bulgarian_number(INPUT_SIZE * hidden_size + hidden_size * OUTPUT_SIZE),
                    "умножения на агент за един тик"))
    for x, number, label in big_numbers:
        _stat(canvas, x, CONTENT_TOP, number, label, 5.5)

    seconds_scale = (SLIDE_WIDTH - MARGIN - TIME_BAR_LEFT - 1.0) / MEASURED_LATE_GENERATION_SECONDS
    rows = ((MEASURED_EARLY_GENERATION, MEASURED_EARLY_GENERATION_SECONDS),
            (MEASURED_LATE_GENERATION, MEASURED_LATE_GENERATION_SECONDS))
    for index, (generation, seconds) in enumerate(rows):
        top = TIME_BARS_TOP + index * (TIME_BAR_HEIGHT + BLOCK_GAP)
        canvas.text(MARGIN, top, TIME_BAR_LEFT - MARGIN - 0.2, TIME_BAR_HEIGHT, f"Поколение {generation}",
                    BODY_SIZE, TEXT, anchor=MSO_ANCHOR.MIDDLE)
        canvas.card(TIME_BAR_LEFT, top, seconds * seconds_scale, TIME_BAR_HEIGHT, fill=SURFACE_EDGE, rounded=False)
        canvas.card(TIME_BAR_LEFT, top, MEASURED_NEXT_GENOMES_SECONDS * seconds_scale, TIME_BAR_HEIGHT, fill=GOLD,
                    rounded=False)
        canvas.text(TIME_BAR_LEFT + seconds * seconds_scale + 0.15, top, 1.0, TIME_BAR_HEIGHT,
                    f"{bulgarian_number(seconds, 1)} s", BODY_SIZE, TEXT, BODY_SEMIBOLD_FONT, anchor=MSO_ANCHOR.MIDDLE)
    legend_top = TIME_BARS_TOP + 2 * (TIME_BAR_HEIGHT + BLOCK_GAP) + 0.05
    for index, (colour, label) in enumerate(((GOLD, "генетичен алгоритъм"),
                                              (SURFACE_EDGE, "симулация на играта и мрежите"))):
        x = TIME_BAR_LEFT + index * TIME_LEGEND_ITEM_WIDTH
        canvas.card(x, legend_top + 0.05, 0.22, 0.22, fill=colour, rounded=False)
        canvas.text(x + 0.35, legend_top, TIME_LEGEND_ITEM_WIDTH - 0.35, 0.35, label, LABEL_SIZE, MUTED)


def results_slide(deck: DeckBuilder, canvas: SlideCanvas) -> None:
    facts = deck.facts
    deck.headline(canvas, f"Първият агент стига флага в *поколение {facts.first_flag_generation}*")
    chart_data = XyChartData()
    for name, values in (("най-добра", facts.best_fitness), ("средна", facts.average_fitness)):
        series = chart_data.add_series(name)
        for generation, value in zip(facts.generations, values):
            series.add_data_point(generation, value)
    marker = chart_data.add_series("първи флаг")
    marker.add_data_point(facts.first_flag_generation, 0)
    marker.add_data_point(facts.first_flag_generation, RESULTS_FITNESS_AXIS_MAXIMUM)

    frame_width = CONTENT_WIDTH
    chart = canvas.slide.shapes.add_chart(
        XL_CHART_TYPE.XY_SCATTER_LINES_NO_MARKERS, Inches(MARGIN), Inches(RESULTS_CHART_TOP), Inches(frame_width),
        Inches(RESULTS_CHART_HEIGHT), chart_data).chart
    _quiet_chart(chart)
    _place_plot_area(chart)
    styles = ((GOLD, RESULTS_BEST_LINE_WIDTH_PT, False), (SKY, RESULTS_AVERAGE_LINE_WIDTH_PT, False),
              (GREEN, RESULTS_MARKER_LINE_WIDTH_PT, True))
    for series, (colour, width, dashed) in zip(chart.plots[0].series, styles):
        series.smooth = False
        series.format.line.color.rgb = RGBColor.from_string(colour)
        series.format.line.width = Pt(width)
        if dashed:
            series.format.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    for axis, maximum, step in ((chart.value_axis, RESULTS_FITNESS_AXIS_MAXIMUM, RESULTS_FITNESS_AXIS_STEP),
                                (chart.category_axis, facts.last_generation, RESULTS_GENERATION_AXIS_STEP)):
        axis.minimum_scale, axis.maximum_scale, axis.major_unit = 0, maximum, step
        axis.major_tick_mark = XL_TICK_MARK.NONE
        axis.tick_label_position = XL_TICK_LABEL_POSITION.LOW
        axis.format.line.color.rgb = RGBColor.from_string(SURFACE_EDGE)
        _axis_labels(axis, MUTED, CAPTION_SIZE)
    chart.value_axis.has_major_gridlines = True
    gridlines = chart.value_axis.major_gridlines.format.line
    gridlines.color.rgb = RGBColor.from_string(SURFACE_EDGE)
    gridlines.width = Pt(RESULTS_GRID_LINE_WIDTH_PT)
    chart.category_axis.has_major_gridlines = False
    chart.value_axis.tick_labels.number_format = RESULTS_AXIS_NUMBER_FORMAT
    chart.value_axis.tick_labels.number_format_is_linked = False

    def to_slide(generation: float, fitness: float) -> tuple[float, float]:
        plot_left = MARGIN + frame_width * RESULTS_PLOT_LEFT
        plot_top = RESULTS_CHART_TOP + RESULTS_CHART_HEIGHT * RESULTS_PLOT_TOP
        return (plot_left + frame_width * RESULTS_PLOT_WIDTH * generation / facts.last_generation,
                plot_top + RESULTS_CHART_HEIGHT * RESULTS_PLOT_HEIGHT * (1 - fitness / RESULTS_FITNESS_AXIS_MAXIMUM))

    end_labels = ((facts.best_fitness[-1], "най-добра", GOLD), (facts.average_fitness[-1], "средна", SKY))
    for value, label, colour in end_labels:
        x, y = to_slide(facts.last_generation, value)
        canvas.text(x + 0.15, y - 0.17, 1.5, 0.34, label, BODY_SIZE, colour, BODY_SEMIBOLD_FONT,
                    anchor=MSO_ANCHOR.MIDDLE)
    marker_x, marker_y = to_slide(facts.first_flag_generation, RESULTS_FITNESS_AXIS_MAXIMUM)
    canvas.text(marker_x + 0.12, marker_y, 3.2, 0.34, f"поколение {facts.first_flag_generation}: първият флаг",
                LABEL_SIZE, GREEN, BODY_SEMIBOLD_FONT)
    axis_label_x, axis_label_y = to_slide(0, RESULTS_FITNESS_AXIS_MAXIMUM)
    canvas.text(axis_label_x - 1.3, axis_label_y - 0.4, 1.2, 0.3, "годност", CAPTION_SIZE, MUTED,
                align=PP_ALIGN.RIGHT)


def replays_slide(deck: DeckBuilder, canvas: SlideCanvas) -> None:
    facts = deck.facts
    deck.headline(canvas, "От хаос в поколение 1 към *цел* в поколение 200")
    screenshot_height = REPLAY_SCREENSHOT_WIDTH / _screenshot_aspect()
    for index, (generation, seconds) in enumerate(REPLAY_GENERATIONS):
        x = MARGIN + index * (REPLAY_SCREENSHOT_WIDTH + BLOCK_GAP)
        _framed_picture(canvas, FIGURES_FOLDER / f"screenshot_ghosts_generation_{generation}.png", x, CONTENT_TOP + 0.1,
                        REPLAY_SCREENSHOT_WIDTH, screenshot_height,
                        f"Повторение на поколение {generation}, {seconds} s след началото")
        canvas.text(x, CONTENT_TOP + 0.1 + screenshot_height + 0.2, REPLAY_SCREENSHOT_WIDTH, 0.6,
                    [[Run(f"Поколение {generation}", TEXT, BODY_SEMIBOLD_FONT)], f"{seconds} s след старта"],
                    BODY_SIZE, MUTED)
    right = MARGIN + 2 * REPLAY_SCREENSHOT_WIDTH + BLOCK_GAP + 0.8
    population = bulgarian_number(facts.settings["population_size"])
    _stat(canvas, right, CONTENT_TOP + 0.1, str(facts.last_finishers),
          f"от {population} агента стигат флага в поколение {facts.last_generation}", SLIDE_WIDTH - MARGIN - right)
    _stat(canvas, right, CONTENT_TOP + 2.0, f"{bulgarian_number(facts.fastest_finish_seconds, 1)} s",
          "най-бързото преминаване на нивото", SLIDE_WIDTH - MARGIN - right)


def verdict_slide(deck: DeckBuilder, canvas: SlideCanvas) -> None:
    deck.headline(canvas, "Учи се без верни отговори, но *плаща с много опити*")
    columns = (
        ("+ Силни страни", GREEN, (("Без градиенти", "стига едно число на опит"),
                                   ("Паралелно", "8 процеса играят едновременно"),
                                   ("Възпроизводимо", "едно семе – същият резултат"))),
        ("− Слаби страни", PURPLE, (("Разхищава данни", "от цял опит остава едно число"),
                                    ("Много настройки", "подбрани с експерименти"),
                                    ("Научава нивото", "не умението да играе изобщо"))),
    )
    card_width = (CONTENT_WIDTH - BLOCK_GAP) / 2
    for index, (title, colour, items) in enumerate(columns):
        x = MARGIN + index * (card_width + BLOCK_GAP)
        top = CONTENT_TOP + 0.15
        canvas.card(x, top, card_width, VERDICT_CARD_HEIGHT)
        canvas.pixel_text(title, x + 0.45, top + 0.4, MEDIUM_NUMBER_SIZE * 0.8, colour)
        for item_index, (name, detail) in enumerate(items):
            item_top = top + 1.25 + item_index * 0.95
            canvas.card(x + 0.45, item_top + 0.1, 0.14, 0.14, fill=colour, rounded=False)
            canvas.text(x + 0.8, item_top, card_width - 1.2, 0.8,
                        [[Run(name, TEXT, BODY_SEMIBOLD_FONT)], detail], BODY_SIZE + 2, MUTED, line_spacing=1.0)


def thanks_slide(deck: DeckBuilder, canvas: SlideCanvas) -> None:
    centre = SLIDE_WIDTH / 2
    title = canvas.pixel_text("Благодаря!", centre, THANKS_TITLE_TOP, TITLE_SIZE, GOLD, align=PP_ALIGN.CENTER)
    question_top = THANKS_TITLE_TOP + title.height + BLOCK_GAP
    question = canvas.pixel_text("Въпроси?", centre, question_top, HEADLINE_SIZE, TEXT, align=PP_ALIGN.CENTER)
    canvas.text(MARGIN, question_top + question.height + 0.45, CONTENT_WIDTH, 0.4, REPO_URL, BODY_SIZE, MUTED,
                CODE_FONT, align=PP_ALIGN.CENTER)

    ground_top = SLIDE_HEIGHT - THANKS_TILE_SIZE
    tiles_across = int(SLIDE_WIDTH / THANKS_TILE_SIZE) + 1
    canvas.picture(_tile_row(GROUND_SPRITE, tiles_across), 0, ground_top, width=tiles_across * THANKS_TILE_SIZE,
                   alt_text="")
    block_top = ground_top - 4.2 * THANKS_TILE_SIZE
    scene = ((QUESTION_BLOCK_SPRITE, THANKS_HERO_LEFT, block_top),
             (HERO_JUMP_SPRITE, THANKS_HERO_LEFT, block_top + THANKS_TILE_SIZE),  # bumping the "?" block
             (ENEMY_SPRITE, SLIDE_WIDTH - THANKS_ENEMY_RIGHT, ground_top - THANKS_TILE_SIZE))
    for sprite, x, y in scene:
        picture, _, _ = sprite_picture(sprite, PIXEL_SPRITE_SCALE)
        canvas.picture(picture, x, y, THANKS_TILE_SIZE, THANKS_TILE_SIZE, alt_text="")


SLIDES = [
    ("title", title_slide), ("goal", goal_slide), ("idea", idea_slide), ("observation", observation_slide),
    ("network", network_slide), ("genome", genome_slide), ("cycle", cycle_slide), ("fitness", fitness_slide),
    ("boundary", boundary_slide), ("time", time_slide), ("results", results_slide), ("replays", replays_slide),
    ("verdict", verdict_slide), ("thanks", thanks_slide),
]


# Shared pieces ----------------------------------------------------------------------------------------

def _stat(canvas: SlideCanvas, x, y, number: str, label: str, width) -> None:
    """A big gold number with a short label under it."""
    rendered = canvas.pixel_text(number, x, y, BIG_NUMBER_SIZE, GOLD)
    canvas.text(x, y + rendered.height + 0.12, width, 0.5, label, BODY_SIZE, MUTED)


def _framed_picture(canvas: SlideCanvas, image_file, x, y, width, height, alt_text: str) -> None:
    picture = canvas.picture(str(image_file), x, y, width, height, alt_text)
    picture.line.color.rgb = RGBColor.from_string(SURFACE_EDGE)
    picture.line.width = Pt(FRAME_WIDTH_PT)


def _screenshot_aspect() -> float:
    with Image.open(FIGURES_FOLDER / "screenshot_sprite_view.png") as screenshot:
        return screenshot.width / screenshot.height


def _grid_aspect() -> float:
    """The observation grid picture's height over its width."""
    step = GRID_CELL_PIXELS + GRID_CELL_GAP_PIXELS
    rows, columns = len(OBSERVATION_GRID_ROWS), len(OBSERVATION_GRID_ROWS[0])
    return (rows * step - GRID_CELL_GAP_PIXELS) / (columns * step - GRID_CELL_GAP_PIXELS)


def _tile_row(sprite_file, count: int) -> io.BytesIO:
    tile = Image.open(sprite_file).convert("RGBA")
    row = Image.new("RGBA", (tile.width * count, tile.height))
    for index in range(count):
        row.paste(tile, (index * tile.width, 0))
    return png_bytes(row.resize((row.width * PIXEL_SPRITE_SCALE, row.height * PIXEL_SPRITE_SCALE),
                                Image.Resampling.NEAREST))


def _quiet_chart(chart) -> None:
    """No title, legend or background: the slide around the chart says what it shows."""
    chart.has_title = False
    chart.has_legend = False
    chart.font.name = BODY_FONT
    chart.font.color.rgb = RGBColor.from_string(MUTED)
    chart_space = chart._chartSpace
    for owner in (chart_space, chart_space.chart.plotArea):
        properties = owner.find(qn("c:spPr"))
        if properties is None:
            properties = etree.SubElement(owner, qn("c:spPr"))
            if owner is chart_space:  # c:spPr comes right after c:chart in the chart space
                chart_space.chart.addnext(properties)
        properties.clear()
        etree.SubElement(properties, qn("a:noFill"))
        line = etree.SubElement(properties, qn("a:ln"))
        etree.SubElement(line, qn("a:noFill"))


def _axis_labels(axis, colour: str, size: float) -> None:
    font = axis.tick_labels.font
    font.size, font.name, font.color.rgb = Pt(size), BODY_FONT, RGBColor.from_string(colour)


def _place_plot_area(chart) -> None:
    """Fix the plot area's inner rectangle so labels can be placed on the plot from outside the chart."""
    plot_area = chart._chartSpace.chart.plotArea
    old_layout = plot_area.find(qn("c:layout"))
    if old_layout is not None:
        plot_area.remove(old_layout)
    layout = etree.Element(qn("c:layout"))
    manual = etree.SubElement(layout, qn("c:manualLayout"))
    for tag, value in (("layoutTarget", "inner"), ("xMode", "edge"), ("yMode", "edge"),
                       ("x", RESULTS_PLOT_LEFT), ("y", RESULTS_PLOT_TOP),
                       ("w", RESULTS_PLOT_WIDTH), ("h", RESULTS_PLOT_HEIGHT)):
        etree.SubElement(manual, qn(f"c:{tag}"), val=str(value))
    plot_area.insert(0, layout)


def main() -> None:
    deck = DeckBuilder(read_run_facts(RESULTS_RUN))
    deck.build(SLIDES)
    deck.presentation.save(PRESENTATION_OUTPUT)
    print(f"wrote {PRESENTATION_OUTPUT}")


if __name__ == "__main__":
    main()
