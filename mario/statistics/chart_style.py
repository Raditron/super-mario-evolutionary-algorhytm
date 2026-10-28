"""The look every chart shares, and how one is written: matplotlib's Agg canvas, never
pyplot, so stats runs headless and keeps no global figure state."""

from pathlib import Path

from matplotlib.axes import Axes
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator

from mario.constants.statistics import (
    CHART_DPI,
    CHART_GRID_COLOUR,
    CHART_MUTED_TEXT_COLOUR,
    CHART_SURFACE_COLOUR,
    CHART_TEXT_COLOUR,
    GENERATION_AXIS_LABEL,
    LABEL_FONT_SIZE_POINTS,
    LEGEND_BESIDE_PANEL_ANCHOR,
    TITLE_FONT_SIZE_POINTS,
)


def new_chart(size_inches: tuple[float, float], panel_count: int = 1) -> tuple[Figure, list[Axes]]:
    """A figure on the Agg canvas with panel_count panels stacked over one generation axis."""
    figure = Figure(figsize=size_inches, dpi=CHART_DPI, facecolor=CHART_SURFACE_COLOUR, layout="constrained")
    FigureCanvasAgg(figure)
    panels = figure.subplots(panel_count, 1, sharex=True, squeeze=False)[:, 0]
    for panel in panels:
        _style(panel)
    panels[-1].set_xlabel(GENERATION_AXIS_LABEL, fontsize=LABEL_FONT_SIZE_POINTS, color=CHART_MUTED_TEXT_COLOUR)
    return figure, list(panels)


def name_panel(panel: Axes, title: str, value_label: str) -> None:
    panel.set_title(title, fontsize=TITLE_FONT_SIZE_POINTS, color=CHART_TEXT_COLOUR, loc="left")
    panel.set_ylabel(value_label, fontsize=LABEL_FONT_SIZE_POINTS, color=CHART_MUTED_TEXT_COLOUR)


def add_legend(panel: Axes) -> None:
    panel.legend(frameon=False, fontsize=LABEL_FONT_SIZE_POINTS, labelcolor=CHART_TEXT_COLOUR)


def add_legend_beside_stack(panel: Axes) -> None:
    """For a stacked chart, whose fills leave no room inside: right of the panel, top entry the top layer."""
    handles, labels = panel.get_legend_handles_labels()
    panel.legend(handles[::-1], labels[::-1], loc="upper left", bbox_to_anchor=LEGEND_BESIDE_PANEL_ANCHOR,
                 frameon=False, fontsize=LABEL_FONT_SIZE_POINTS, labelcolor=CHART_TEXT_COLOUR)


def save_chart(figure: Figure, path: Path) -> None:
    figure.savefig(path, facecolor=CHART_SURFACE_COLOUR)


def _style(panel: Axes) -> None:
    panel.set_facecolor(CHART_SURFACE_COLOUR)
    panel.grid(axis="y", color=CHART_GRID_COLOUR)
    panel.set_axisbelow(True)
    panel.xaxis.set_major_locator(MaxNLocator(integer=True))
    panel.tick_params(colors=CHART_MUTED_TEXT_COLOUR, labelsize=LABEL_FONT_SIZE_POINTS)
    for side in ("top", "right"):
        panel.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        panel.spines[side].set_color(CHART_GRID_COLOUR)
