"""The report's four flowcharts (блок-схеми), drawn with matplotlib into figures/:
the training run, one generation's breeding, an agent's decision and the fitness function.

py docs/coursework/flowcharts.py
"""

from dataclasses import dataclass

import matplotlib

matplotlib.use("Agg")
from matplotlib import pyplot
from matplotlib.patches import FancyBboxPatch, Polygon

from report_constants import (
    FIGURES_FOLDER, FLOWCHART_ARROW_HEAD_SIZE, FLOWCHART_BORDER_COLOUR, FLOWCHART_BRANCH_MERGE_HEIGHT,
    FLOWCHART_CHARACTER_WIDTH, FLOWCHART_COLOURS, FLOWCHART_COLUMN_GAP, FLOWCHART_DIAMOND_HEIGHT_PER_TEXT_HEIGHT,
    FLOWCHART_DIAMOND_WIDTH_PER_TEXT_WIDTH, FLOWCHART_DPI, FLOWCHART_EDGE_COLOUR, FLOWCHART_EDGE_LABEL_OFFSET,
    FLOWCHART_FONT_FAMILY, FLOWCHART_FONT_SIZE, FLOWCHART_INCHES_PER_UNIT, FLOWCHART_LINE_HEIGHT,
    FLOWCHART_LINE_WIDTH, FLOWCHART_MARGIN, FLOWCHART_NODE_MINIMUM_WIDTH, FLOWCHART_NODE_PADDING_X,
    FLOWCHART_NODE_PADDING_Y, FLOWCHART_PARALLELOGRAM_SLANT, FLOWCHART_ROW_GAP, FLOWCHART_TERMINAL_ROUNDING,
    FLOWCHART_TEXT_LINE_SPACING,
)

TERMINAL, PROCESS, DECISION, DATA = "terminal", "process", "decision", "data"


@dataclass
class Node:
    kind: str
    text: str
    centre_x: float = 0.0
    centre_y: float = 0.0  # grows downwards

    @property
    def width(self) -> float:
        text_width = max(len(line) for line in self.text.split("\n")) * FLOWCHART_CHARACTER_WIDTH
        if self.kind == DECISION:
            return text_width * FLOWCHART_DIAMOND_WIDTH_PER_TEXT_WIDTH + FLOWCHART_NODE_PADDING_X
        return max(FLOWCHART_NODE_MINIMUM_WIDTH, text_width + 2 * FLOWCHART_NODE_PADDING_X)

    @property
    def height(self) -> float:
        text_height = len(self.text.split("\n")) * FLOWCHART_LINE_HEIGHT
        if self.kind == DECISION:
            return text_height * FLOWCHART_DIAMOND_HEIGHT_PER_TEXT_HEIGHT + FLOWCHART_NODE_PADDING_Y
        return text_height + 2 * FLOWCHART_NODE_PADDING_Y

    @property
    def half_width(self) -> float:
        """Half the width it takes up, a parallelogram's slant included."""
        return self.width / 2 + (FLOWCHART_PARALLELOGRAM_SLANT if self.kind == DATA else 0)

    @property
    def bottom(self) -> float:
        return self.centre_y + self.height / 2

    def port(self, side: str) -> tuple[float, float]:
        """Where an edge leaves or enters: the middle of the side named."""
        half_width, half_height = self.width / 2, self.height / 2
        return {
            "top": (self.centre_x, self.centre_y - half_height),
            "bottom": (self.centre_x, self.centre_y + half_height),
            "left": (self.centre_x - half_width, self.centre_y),
            "right": (self.centre_x + half_width, self.centre_y),
        }[side]


@dataclass
class Edge:
    start: str
    end: str
    exit_side: str
    enter_side: str
    label: str | None
    via_x: float | None


class Flowchart:
    """Nodes stacked in columns (or set beside one another); edges routed with right angles between their ports."""

    def __init__(self) -> None:
        self._nodes: dict[str, Node] = {}
        self._edges: list[Edge] = []

    def stack(self, centre_x: float, top_y: float, entries: list[tuple[str, str, str]]) -> float:
        """(name, kind, text) nodes one below the other from top_y down; returns the bottom of the last."""
        for name, kind, text in entries:
            node = Node(kind, text, centre_x)
            node.centre_y = top_y + node.height / 2
            self._nodes[name] = node
            top_y = node.bottom + FLOWCHART_ROW_GAP
        return top_y - FLOWCHART_ROW_GAP

    def beside(self, name: str, kind: str, text: str, anchor_names: list[str], centre_y: float,
               side: int = 1) -> None:
        """A node level with centre_y, clear of the widest of anchor_names on the side given (+1 right, −1 left)."""
        node = Node(kind, text, centre_y=centre_y)
        clearance = max(self._nodes[anchor].half_width for anchor in anchor_names)
        anchor_x = self._nodes[anchor_names[0]].centre_x
        node.centre_x = anchor_x + side * (clearance + FLOWCHART_COLUMN_GAP + node.half_width)
        self._nodes[name] = node

    def side_line_x(self, names: list[str], side: int) -> float:
        """The x of a loop line running past these nodes on one side (+1 right, −1 left)."""
        if side > 0:
            return max(self._nodes[name].centre_x + self._nodes[name].half_width for name in names) \
                + FLOWCHART_COLUMN_GAP / 2
        return min(self._nodes[name].centre_x - self._nodes[name].half_width for name in names) \
            - FLOWCHART_COLUMN_GAP / 2

    def node(self, name: str) -> Node:
        return self._nodes[name]

    def connect(self, start: str, end: str, exit_side: str = "bottom", enter_side: str = "top",
                label: str | None = None, via_x: float | None = None) -> None:
        self._edges.append(Edge(start, end, exit_side, enter_side, label, via_x))

    def chain(self, *names: str) -> None:
        """Each node straight down into the next."""
        for start, end in zip(names, names[1:]):
            self.connect(start, end)

    def _route(self, edge: Edge) -> list[tuple[float, float]]:
        start = self._nodes[edge.start].port(edge.exit_side)
        end = self._nodes[edge.end].port(edge.enter_side)
        horizontal_exit = edge.exit_side in ("left", "right")
        horizontal_enter = edge.enter_side in ("left", "right")
        if edge.via_x is not None:
            return [start, (edge.via_x, start[1]), (edge.via_x, end[1]), end]
        if horizontal_exit and not horizontal_enter:
            return [start, (end[0], start[1]), end]
        if not horizontal_exit and horizontal_enter:
            return [start, (start[0], end[1]), end]
        if start[0] != end[0] and not horizontal_exit:
            merge_y = end[1] - FLOWCHART_BRANCH_MERGE_HEIGHT
            return [start, (start[0], merge_y), (end[0], merge_y), end]
        return [start, end]

    def save(self, file_name: str) -> None:
        routes = [self._route(edge) for edge in self._edges]
        all_x = [node.centre_x + side * node.half_width for node in self._nodes.values() for side in (-1, 1)]
        all_x += [x for route in routes for x, _ in route]
        all_y = [node.centre_y + side * node.height / 2 for node in self._nodes.values() for side in (-1, 1)]
        left, right = min(all_x) - FLOWCHART_MARGIN, max(all_x) + FLOWCHART_MARGIN
        top, bottom = min(all_y) - FLOWCHART_MARGIN, max(all_y) + FLOWCHART_MARGIN

        figure = pyplot.figure(figsize=((right - left) * FLOWCHART_INCHES_PER_UNIT,
                                        (bottom - top) * FLOWCHART_INCHES_PER_UNIT))
        axes = figure.add_axes((0, 0, 1, 1))
        axes.set_xlim(left, right)
        axes.set_ylim(bottom, top)  # y grows downwards
        axes.set_axis_off()
        for node in self._nodes.values():
            _draw_node(axes, node)
        for edge, route in zip(self._edges, routes):
            _draw_edge(axes, edge, route)
        FIGURES_FOLDER.mkdir(exist_ok=True)
        figure.savefig(FIGURES_FOLDER / file_name, dpi=FLOWCHART_DPI)
        pyplot.close(figure)


def _draw_node(axes, node: Node) -> None:
    style = dict(facecolor=FLOWCHART_COLOURS[node.kind], edgecolor=FLOWCHART_BORDER_COLOUR,
                 linewidth=FLOWCHART_LINE_WIDTH)
    left, right = node.port("left")[0], node.port("right")[0]
    top, bottom = node.port("top")[1], node.port("bottom")[1]
    if node.kind == TERMINAL:
        rounding = min(FLOWCHART_TERMINAL_ROUNDING, node.height / 2)
        axes.add_patch(FancyBboxPatch((left, top), node.width, node.height,
                                      boxstyle=f"round,pad=0,rounding_size={rounding}", **style))
    elif node.kind == PROCESS:
        axes.add_patch(FancyBboxPatch((left, top), node.width, node.height, boxstyle="square,pad=0", **style))
    elif node.kind == DECISION:
        axes.add_patch(Polygon([node.port("top"), node.port("right"), node.port("bottom"), node.port("left")],
                               closed=True, **style))
    else:
        slant = FLOWCHART_PARALLELOGRAM_SLANT
        axes.add_patch(Polygon([(left + slant, top), (right + slant, top), (right - slant, bottom),
                                (left - slant, bottom)], closed=True, **style))
    axes.text(node.centre_x, node.centre_y, node.text, ha="center", va="center",
              fontsize=FLOWCHART_FONT_SIZE, linespacing=FLOWCHART_TEXT_LINE_SPACING)


def _draw_edge(axes, edge: Edge, route: list[tuple[float, float]]) -> None:
    line_style = dict(color=FLOWCHART_EDGE_COLOUR, linewidth=FLOWCHART_LINE_WIDTH)
    for (start_x, start_y), (end_x, end_y) in zip(route[:-2], route[1:-1]):
        axes.plot([start_x, end_x], [start_y, end_y], solid_capstyle="round", **line_style)
    axes.annotate("", xy=route[-1], xytext=route[-2],
                  arrowprops=dict(arrowstyle="-|>", mutation_scale=FLOWCHART_ARROW_HEAD_SIZE,
                                  shrinkA=0, shrinkB=0, **line_style))
    if edge.label:
        (start_x, start_y), (next_x, _) = route[0], route[1]
        offset = FLOWCHART_EDGE_LABEL_OFFSET
        if next_x != start_x:  # leaves sideways: label above the line
            going_right = next_x > start_x
            axes.text(start_x + offset * (1 if going_right else -1), start_y - offset, edge.label,
                      ha="left" if going_right else "right", va="bottom",
                      fontsize=FLOWCHART_FONT_SIZE, style="italic")
        else:  # leaves downwards: label beside the line
            axes.text(start_x + offset, start_y + offset, edge.label, ha="left", va="top",
                      fontsize=FLOWCHART_FONT_SIZE, style="italic")


def training_run() -> None:
    chart = Flowchart()
    column = ["start", "config", "create", "initial", "play", "fitness", "record", "more", "end"]
    chart.stack(0, 0, [
        ("start", TERMINAL, "Начало:\npy -m mario train"),
        ("config", DATA, "Чете config.toml\n([run] и [algorithm])"),
        ("create", PROCESS, "algorithm =\ncreate_algorithm(settings)"),
        ("initial", PROCESS, "rng = default_rng(seed)\ngenomes =\ninitial_genomes(P, rng)\ng = 1"),
        ("play", PROCESS, "8 процеса изиграват\nP опита: build_brain,\ndecide() на всеки тик"),
        ("fitness", PROCESS, "fitnesses[i] =\nfitness(attempt_result[i])\nза всеки агент i"),
        ("record", DATA, "Записва results.csv,\ngeneration_times.csv,\nbest_genome.npy,\ncontroller_logs.npz"),
        ("more", DECISION, "g < G?"),
        ("end", TERMINAL, "Край на обучението"),
    ])
    chart.beside("next", PROCESS, "genomes = next_genomes(\ngenomes, fitnesses, rng)\ng = g + 1",
                 column, chart.node("more").centre_y)
    chart.chain(*column[:-1])
    chart.connect("more", "next", "right", "left", label="да")
    chart.connect("next", "play", "top", "right")
    chart.connect("more", "end", label="не")
    chart.save("flowchart_training_run.png")


def next_generation() -> None:
    chart = Flowchart()
    upper = ["start", "elites", "select", "pairs", "more", "crossover"]
    upper_bottom = chart.stack(0, 0, [
        ("start", TERMINAL, "next_genomes(genomes,\nfitnesses, rng)"),
        ("elites", PROCESS, "elites = копия на E-те\nнай-годни генома\n(стабилно сортиране)"),
        ("select", PROCESS, "Турнирна селекция:\n2·(P − E) турнира по\nk случайни агента"),
        ("pairs", PROCESS, "Победителите се групират\nпо двойки (A, B)"),
        ("more", DECISION, "Има ли още\nдвойка (A, B)?"),
        ("crossover", DECISION, "rng.random() <\ncrossover_rate?"),
    ])
    branch_top = upper_bottom + FLOWCHART_ROW_GAP
    uniform_text = "Равномерно\nкръстосване:\nвсеки ген от\nA или B (p = 0,5)"
    branch_centre_y = branch_top + Node(PROCESS, uniform_text).height / 2
    chart.beside("uniform", PROCESS, uniform_text, ["crossover"], branch_centre_y, side=-1)
    chart.beside("clone", PROCESS, "Детето =\nкопие на A", ["crossover"], branch_centre_y, side=1)
    lower_top = chart.node("uniform").bottom + FLOWCHART_ROW_GAP + FLOWCHART_BRANCH_MERGE_HEIGHT
    chart.stack(0, lower_top, [
        ("mutate", PROCESS, "Гаусова мутация: всеки\nген с вероятност\nmutation_rate + N(0, σ)"),
        ("append", PROCESS, "Детето се добавя\nкъм children"),
    ])
    chart.beside("return", TERMINAL, "return elites\n+ children", upper, chart.node("more").centre_y)
    chart.chain(*upper[:-1])
    chart.connect("more", "crossover", label="да")
    chart.connect("more", "return", "right", "left", label="не")
    chart.connect("crossover", "uniform", "left", "top", label="да")
    chart.connect("crossover", "clone", "right", "top", label="не")
    chart.connect("uniform", "mutate")
    chart.connect("clone", "mutate")
    chart.connect("mutate", "append")
    chart.connect("append", "more", "left", "left", via_x=chart.side_line_x(upper + ["uniform", "append"], -1))
    chart.save("flowchart_next_generation.png")


def agent_decision() -> None:
    chart = Flowchart()
    column = ["start", "input", "more", "hidden", "output", "store"]
    chart.stack(0, 0, [
        ("start", TERMINAL, "decide(observations)\n— един тик"),
        ("input", DATA, "Наблюдения: агенти × 160\n(156 клетки + 4 числа)"),
        ("more", DECISION, "Има ли още\nагент i?"),
        ("hidden", PROCESS, "h = tanh(x_i · W1 + b1)\n(скрит слой, 24 неврона)"),
        ("output", PROCESS, "y = tanh(h · W2 + b2)\n(изходен слой, 5 неврона)"),
        ("store", PROCESS, "Ред i на изходите = y"),
    ])
    chart.beside("threshold", PROCESS, "натиснат[i, j] =\nизход[i, j] > праг\n(праг = 0,0)",
                 column, chart.node("more").centre_y)
    threshold = chart.node("threshold")
    chart.stack(threshold.centre_x, threshold.bottom + FLOWCHART_ROW_GAP, [
        ("presses", DATA, "Натискания: агенти × 5\n(ляво, дясно, долу,\nскок, бягане)"),
        ("end", TERMINAL, "Към симулацията:\nследващ тик"),
    ])
    chart.chain("start", "input", "more")
    chart.connect("more", "hidden", label="да")
    chart.chain("hidden", "output", "store")
    chart.connect("store", "more", "left", "left", via_x=chart.side_line_x(column, -1))
    chart.connect("more", "threshold", "right", "left", label="не")
    chart.chain("threshold", "presses", "end")
    chart.save("flowchart_agent_decision.png")


def fitness_function() -> None:
    chart = Flowchart()
    column = ["start", "base", "flag", "bonus", "end"]
    chart.stack(0, 0, [
        ("start", TERMINAL, "score(attempt_result)"),
        ("base", PROCESS, "f = furthest_x +\ncoin_reward · coins_collected"),
        ("flag", DECISION, "end_reason ==\nREACHED_FLAG?"),
        ("bonus", PROCESS, "f = f + flag_reward −\ntime_reward · ticks_elapsed"),
        ("end", TERMINAL, "return f"),
    ])
    chart.chain("start", "base", "flag")
    chart.connect("flag", "bonus", label="да")
    chart.connect("bonus", "end")
    chart.connect("flag", "end", "right", "right", label="не", via_x=chart.side_line_x(column, 1))
    chart.save("flowchart_fitness.png")


if __name__ == "__main__":
    pyplot.rcParams["font.family"] = FLOWCHART_FONT_FAMILY
    training_run()
    next_generation()
    agent_decision()
    fitness_function()
