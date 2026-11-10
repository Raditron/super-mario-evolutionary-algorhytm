"""Drawing on the presentation's slides: pixel-font text rendered into pictures (so it looks the same
on any computer), the observation grid, the genome and sprite pictures, and the shapes and text
boxes every slide is composed of. All positions and sizes are in inches."""

import io
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from fontTools.ttLib import TTFont
from lxml import etree
from PIL import Image, ImageDraw, ImageFont
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

from presentation_constants import (
    BODY_FONT, CARD_CORNER, GENOME_CLIP_SPREADS, GENOME_GENE_PIXELS, GENOME_PART_GAP_GENES, GOLD,
    GREEN, GRID_CELL_GAP_PIXELS, GRID_CELL_PIXELS, INK, OBSERVATION_GRID_ROWS, PIXEL_FONT_FILE,
    PIXEL_FONT_WEIGHT, PIXEL_HIGHLIGHT_MARK, PIXEL_LINE_SPACING, PIXEL_RENDER_DPI, POINTS_PER_INCH,
    PURPLE, SURFACE, TEXT,
)

NO_BREAK_SPACE = " "
GRID_SOLID, GRID_ENEMY, GRID_HERO = "#", "e", "h"
OPAQUE = 255


def rgb(hex_colour: str) -> tuple[int, int, int]:
    return tuple(int(hex_colour[index:index + 2], 16) for index in (0, 2, 4))


def png_bytes(image: Image.Image) -> io.BytesIO:
    stream = io.BytesIO()
    image.save(stream, format="PNG")
    stream.seek(0)
    return stream


@dataclass(frozen=True)
class PixelPicture:
    stream: io.BytesIO
    width: float
    height: float
    plain_text: str  # the alt text
    line_count: int


class PixelTextRenderer:
    """Draws text in the pixel font into a transparent picture cropped to its ink. Words between two
    highlight marks are drawn in the highlight colour; a no-break space keeps a number with its unit."""

    def __init__(self, font_file: Path = PIXEL_FONT_FILE):
        self._font_file = font_file
        self._characters = set(TTFont(font_file).getBestCmap())
        self._fonts: dict[float, ImageFont.FreeTypeFont] = {}

    def render(self, marked_text: str, size_pt: float, colour: str = TEXT, highlight: str = GOLD,
               max_width: float | None = None) -> PixelPicture:
        plain_text = marked_text.replace(PIXEL_HIGHLIGHT_MARK, "")
        self._check_characters(plain_text)
        font = self._font(size_pt)
        space_width = font.getlength(" ")
        max_width_pixels = max_width * PIXEL_RENDER_DPI if max_width else None
        lines = self._wrap(self._tokens(marked_text), font, space_width, max_width_pixels)

        ascent, descent = font.getmetrics()
        line_height = round((ascent + descent) * PIXEL_LINE_SPACING)
        widths = [self._line_width(line, font, space_width) for line in lines]
        image = Image.new("RGBA", (max(1, round(max(widths))), ascent + descent + line_height * (len(lines) - 1)))
        draw = ImageDraw.Draw(image)
        for line_index, line in enumerate(lines):
            x = 0.0
            for word, highlighted in line:
                draw.text((x, line_index * line_height), word.replace(NO_BREAK_SPACE, " "), font=font,
                          fill=rgb(highlight if highlighted else colour))
                x += font.getlength(word.replace(NO_BREAK_SPACE, " ")) + space_width
        image = image.crop(image.getchannel("A").getbbox())  # the ink only, so it lines up with what is around it
        return PixelPicture(png_bytes(image), image.width / PIXEL_RENDER_DPI, image.height / PIXEL_RENDER_DPI,
                            plain_text.replace(NO_BREAK_SPACE, " ").replace("\n", " "), len(lines))

    def _font(self, size_pt: float) -> ImageFont.FreeTypeFont:
        if size_pt not in self._fonts:
            font = ImageFont.truetype(str(self._font_file), round(size_pt * PIXEL_RENDER_DPI / POINTS_PER_INCH))
            font.set_variation_by_name(PIXEL_FONT_WEIGHT)
            self._fonts[size_pt] = font
        return self._fonts[size_pt]

    def _check_characters(self, text: str) -> None:
        missing = {character for character in text
                   if character not in "\n" + NO_BREAK_SPACE and ord(character) not in self._characters}
        if missing:
            raise ValueError(f"the pixel font has no {''.join(sorted(missing))!r} (in {text!r})")

    @staticmethod
    def _tokens(marked_text: str) -> list[list[tuple[str, bool]]]:
        """Paragraphs of (word, highlighted)."""
        paragraphs = []
        for paragraph in marked_text.split("\n"):
            words = []
            for part_index, part in enumerate(paragraph.split(PIXEL_HIGHLIGHT_MARK)):
                highlighted = part_index % 2 == 1
                words.extend((word, highlighted) for word in part.split(" ") if word)
            paragraphs.append(words)
        return paragraphs

    def _wrap(self, paragraphs, font, space_width, max_width_pixels):
        lines = []
        for words in paragraphs:
            line: list[tuple[str, bool]] = []
            for word in words:
                if line and max_width_pixels and \
                        self._line_width(line + [word], font, space_width) > max_width_pixels:
                    lines.append(line)
                    line = []
                line.append(word)
            lines.append(line)
        return lines

    @staticmethod
    def _line_width(line, font, space_width) -> float:
        widths = [font.getlength(word.replace(NO_BREAK_SPACE, " ")) for word, _ in line]
        return sum(widths) + space_width * max(0, len(widths) - 1)


def observation_grid_picture(hero_sprite: Path | None = None) -> io.BytesIO:
    """The 13 x 12 observation grid: green +1 solid, purple -1 enemy, dark 0 empty; the hero's own
    cell holds its sprite (or gold, without one)."""
    step = GRID_CELL_PIXELS + GRID_CELL_GAP_PIXELS
    rows, columns = len(OBSERVATION_GRID_ROWS), len(OBSERVATION_GRID_ROWS[0])
    image = Image.new("RGBA", (columns * step - GRID_CELL_GAP_PIXELS, rows * step - GRID_CELL_GAP_PIXELS))
    draw = ImageDraw.Draw(image)
    cell_colours = {GRID_SOLID: GREEN, GRID_ENEMY: PURPLE, GRID_HERO: GOLD}
    for row_index, row in enumerate(OBSERVATION_GRID_ROWS):
        for column_index, cell in enumerate(row):
            left, top = column_index * step, row_index * step
            draw.rectangle((left, top, left + GRID_CELL_PIXELS - 1, top + GRID_CELL_PIXELS - 1),
                           fill=rgb(cell_colours.get(cell, SURFACE)))
            if cell == GRID_HERO and hero_sprite:
                draw.rectangle((left, top, left + GRID_CELL_PIXELS - 1, top + GRID_CELL_PIXELS - 1), fill=rgb(SURFACE))
                sprite = Image.open(hero_sprite).convert("RGBA").resize(
                    (GRID_CELL_PIXELS, GRID_CELL_PIXELS), Image.Resampling.NEAREST)
                image.alpha_composite(sprite, (left, top))
    return png_bytes(image)


def genome_picture(genome_parts: list[np.ndarray]) -> tuple[io.BytesIO, list[tuple[float, float]]]:
    """Each part (a 2-D array, rows down) side by side, a gap between parts, every gene a square:
    green positive, purple negative, the ink colour at zero. Also returns each part's horizontal
    span as shares of the picture's width."""
    every_gene = np.concatenate([part.ravel() for part in genome_parts])
    limit = GENOME_CLIP_SPREADS * every_gene.std()
    height_genes = max(part.shape[0] for part in genome_parts)
    width_genes = sum(part.shape[1] for part in genome_parts) + GENOME_PART_GAP_GENES * (len(genome_parts) - 1)
    canvas = np.zeros((height_genes, width_genes, 4), dtype=np.uint8)
    zero, positive, negative = (np.array(rgb(colour), dtype=float) for colour in (SURFACE, GREEN, PURPLE))
    spans = []
    column = 0
    for part in genome_parts:
        strength = np.clip(part / limit, -1, 1)[..., None]
        colours = np.where(strength >= 0, zero + (positive - zero) * strength, zero + (negative - zero) * -strength)
        canvas[:part.shape[0], column:column + part.shape[1], :3] = colours.astype(np.uint8)
        canvas[:part.shape[0], column:column + part.shape[1], 3] = OPAQUE
        spans.append((column / width_genes, (column + part.shape[1]) / width_genes))
        column += part.shape[1] + GENOME_PART_GAP_GENES
    image = Image.fromarray(canvas, "RGBA").resize(
        (width_genes * GENOME_GENE_PIXELS, height_genes * GENOME_GENE_PIXELS), Image.Resampling.NEAREST)
    return png_bytes(image), spans


def sprite_picture(sprite_file: Path, scale: int) -> tuple[io.BytesIO, int, int]:
    """A sprite upscaled with hard pixel edges; also its size in source pixels."""
    sprite = Image.open(sprite_file).convert("RGBA")
    width, height = sprite.size
    return png_bytes(sprite.resize((width * scale, height * scale), Image.Resampling.NEAREST)), width, height


def light_logo_picture(logo_file: Path) -> io.BytesIO:
    """A dark-on-white logo turned into the text colour on a transparent background."""
    darkness = 255 - np.asarray(Image.open(logo_file).convert("L"))
    light = np.zeros((*darkness.shape, 4), dtype=np.uint8)
    light[..., :3] = rgb(TEXT)
    light[..., 3] = darkness
    return png_bytes(Image.fromarray(light, "RGBA"))


@dataclass(frozen=True)
class Run:
    """A stretch of text with its own colour or font."""
    text: str
    colour: str | None = None
    font: str | None = None


class SlideCanvas:
    """One slide and the primitives it is drawn with."""

    def __init__(self, slide, pixel_text: PixelTextRenderer):
        self.slide = slide
        self._pixel_text = pixel_text
        self._shapes = slide.shapes

    def fill_background(self, colour: str = INK) -> None:
        fill = self.slide.background.fill
        fill.solid()
        fill.fore_color.rgb = RGBColor.from_string(colour)

    def card(self, x, y, width, height, fill: str | None = SURFACE, outline: str | None = None,
             outline_width_pt: float = 1.0, rounded: bool = True):
        shape = self._shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE,
                                       Inches(x), Inches(y), Inches(width), Inches(height))
        if rounded:
            shape.adjustments[0] = CARD_CORNER
        if fill:
            shape.fill.solid()
            shape.fill.fore_color.rgb = RGBColor.from_string(fill)
        else:
            shape.fill.background()
        if outline:
            shape.line.color.rgb = RGBColor.from_string(outline)
            shape.line.width = Pt(outline_width_pt)
        else:
            shape.line.fill.background()
        shape.shadow.inherit = False
        return shape

    def dot(self, x, y, size, fill: str, outline: str | None = None):
        shape = self._shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(size), Inches(size))
        shape.fill.solid()
        shape.fill.fore_color.rgb = RGBColor.from_string(fill)
        if outline:
            shape.line.color.rgb = RGBColor.from_string(outline)
        else:
            shape.line.fill.background()
        shape.shadow.inherit = False
        return shape

    def text(self, x, y, width, height, paragraphs, size: float, colour: str = TEXT, font: str = BODY_FONT,
             align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, space_after_pt: float = 0, line_spacing: float = 1.0):
        """paragraphs: a string, or a list of paragraphs each a string or a list of Runs."""
        box = self._shapes.add_textbox(Inches(x), Inches(y), Inches(width), Inches(height))
        frame = box.text_frame
        frame.word_wrap = True
        frame.margin_left = frame.margin_right = frame.margin_top = frame.margin_bottom = 0
        frame.vertical_anchor = anchor
        for index, paragraph_runs in enumerate([paragraphs] if isinstance(paragraphs, str) else paragraphs):
            paragraph = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
            paragraph.alignment = align
            paragraph.space_after = Pt(space_after_pt)
            paragraph.line_spacing = line_spacing
            for run_spec in [Run(paragraph_runs)] if isinstance(paragraph_runs, str) else paragraph_runs:
                run = paragraph.add_run()
                run.text = run_spec.text
                run.font.size = Pt(size)
                run.font.name = run_spec.font or font
                run.font.color.rgb = RGBColor.from_string(run_spec.colour or colour)
        return box

    def picture(self, source, x, y, width=None, height=None, alt_text: str = ""):
        picture = self._shapes.add_picture(source, Inches(x), Inches(y),
                                           Inches(width) if width else None, Inches(height) if height else None)
        picture._element.nvPicPr.cNvPr.set("descr", alt_text)
        return picture

    def pixel_text(self, marked_text: str, x, y, size_pt: float, colour: str = TEXT, max_width=None,
                   align=PP_ALIGN.LEFT) -> PixelPicture:
        """Pixel-font text with its top-left (or top-centre, or top-right) at x, y."""
        rendered = self._pixel_text.render(marked_text, size_pt, colour, max_width=max_width)
        left = {PP_ALIGN.LEFT: x, PP_ALIGN.CENTER: x - rendered.width / 2, PP_ALIGN.RIGHT: x - rendered.width}[align]
        self.picture(rendered.stream, left, y, rendered.width, rendered.height, rendered.plain_text)
        return rendered

    def line(self, x1, y1, x2, y2, colour: str, width_pt: float, arrow: bool = False, dashed: bool = False):
        connector = self._shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
        connector.line.color.rgb = RGBColor.from_string(colour)
        connector.line.width = Pt(width_pt)
        if dashed:
            connector.line.dash_style = MSO_LINE_DASH_STYLE.DASH
        if arrow:
            etree.SubElement(connector.line._get_or_add_ln(), qn("a:tailEnd"), type="triangle")
        return connector

    def notes(self, text: str) -> None:
        self.slide.notes_slide.notes_text_frame.text = text
