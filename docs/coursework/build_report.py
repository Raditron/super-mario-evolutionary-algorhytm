"""Builds the coursework report (.docx) from report.md: the title page, the table of contents,
the text with numbered figures, tables and citations, the sources and the appendix with the
algorithm's code read fresh from the repo. Word, if installed, then fills in the table of contents.

py docs/coursework/build_report.py [--pdf PATH]

report.md understands a small Markdown subset:
  # / ## / ###  headings              - item / 1. item   lists
  | a | b |     tables, after a line   "Таблица: caption {#tbl:key}"
  ![caption](figures/x.png){#fig:key width=11}           a figure (width in cm, optional)
  $$ formula $$                         a centred formula line
  **bold**  *italic*  `code`  ==placeholder==  [@key; @key2] citations  [[fig:key]] / [[tbl:key]] references
  [[references]]  [[appendix]]          where the sources and the code go
"""

import argparse
import io
import re
import subprocess
import sys
from dataclasses import dataclass, field

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_COLOR_INDEX
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt
from PIL import Image

from report_constants import (
    APPENDIX_EXTRA_FILES, APPENDIX_PACKAGE, BODY_FONT, BODY_FONT_SIZE_PT, BODY_LINE_SPACING, BODY_SPACE_AFTER_PT,
    CAPTION_FONT_SIZE_PT, CITY, CODE_FONT, CODE_FONT_SIZE_PT, COURSE_NAME, COURSEWORK_FOLDER, DOCUMENT_KIND,
    FACULTY_NUMBER, FIGURE_CAPTION_PREFIX, FIGURE_MAX_HEIGHT_CM, FIGURE_WIDTH_CM, FIRST_LINE_INDENT_CM, HAND_IN_DATE,
    HEADING_FONT_SIZES_PT, HEADING_SPACE_AFTER_PT, HEADING_SPACE_BEFORE_PT, INLINE_CODE_FONT_SIZE_PT,
    LOGO_HEIGHT_CM, LOGO_IMAGE, PAGE_HEIGHT_CM, PAGE_MARGIN_CM,
    PAGE_WIDTH_CM, PLACEHOLDER_HIGHLIGHT, REPO_ROOT, REPORT_OUTPUT, REPORT_SOURCE, STUDENT_GROUP, STUDENT_NAME,
    TABLE_CAPTION_PREFIX, TABLE_FONT_SIZE_PT, TABLE_HEADER_SHADING, TABLE_OF_CONTENTS_HEADING,
    TABLE_OF_CONTENTS_LEVELS, TITLE_DETAILS_FONT_SIZE_PT, TITLE_FONT_SIZE_PT, TITLE_GAP_LINES,
    TITLE_TOPIC_FONT_SIZE_PT, TOPIC, UNIVERSITY_NAME, TABLE_COLUMN_MINIMUM_WEIGHT,
    TABLE_COLUMN_MAXIMUM_WEIGHT, LIST_INDENT_CM, LIST_HANGING_CM, REFERENCE_HANGING_CM, FORMULA_FONT,
    WATERMARK_IMAGE, WATERMARK_OPACITY, WATERMARK_WIDTH_CM, WORD_PDF_FORMAT,
)
from report_references import REFERENCES

TEXT_WIDTH_CM = PAGE_WIDTH_CM - 2 * PAGE_MARGIN_CM

INLINE_PATTERN = re.compile(
    r"(\*\*.+?\*\*|`[^`]+`|==.+?==|\*[^*\s][^*]*\*|\[@[^\]]+\]|\[\[(?:fig|tbl):[^\]]+\]\])")
LABEL_PATTERN = re.compile(r"\{#((?:fig|tbl):[\w-]+)(?:\s+width=([\d.]+))?\}")
FIGURE_PATTERN = re.compile(r"!\[(.+?)\]\((.+?)\)")
NUMBERED_ITEM_PATTERN = re.compile(r"^\d+\.\s+")
TABLE_DIVIDER_PATTERN = re.compile(r"^\|[\s|:-]+\|$")
HEADING_NUMBER_PATTERN = re.compile(r"^(\d+)\.")


@dataclass
class Block:
    kind: str  # heading, paragraph, bullets, numbered, table, figure, formula, references, appendix
    text: str = ""
    level: int = 0
    items: list = field(default_factory=list)
    label: str | None = None
    width_cm: float | None = None


def parse_markdown(source: str) -> list[Block]:
    """report.md's lines -> blocks, in order."""
    blocks: list[Block] = []
    lines = source.splitlines()
    position = 0
    pending_table_caption: tuple[str, str | None] | None = None
    while position < len(lines):
        line = lines[position].strip()
        if not line:
            position += 1
        elif line.startswith("#"):
            level = len(line) - len(line.lstrip("#"))
            blocks.append(Block("heading", line[level:].strip(), level=level))
            position += 1
        elif line in ("[[references]]", "[[appendix]]"):
            blocks.append(Block(line.strip("[]")))
            position += 1
        elif line.startswith("$$"):
            blocks.append(Block("formula", line.strip("$").strip()))
            position += 1
        elif line.startswith("!["):
            caption, path = FIGURE_PATTERN.match(line).groups()
            label_match = LABEL_PATTERN.search(line)
            width = float(label_match.group(2)) if label_match and label_match.group(2) else None
            blocks.append(Block("figure", path, items=[caption], label=label_match and label_match.group(1),
                                width_cm=width))
            position += 1
        elif line.startswith(TABLE_CAPTION_PREFIX + ":"):
            label_match = LABEL_PATTERN.search(line)
            caption = LABEL_PATTERN.sub("", line[len(TABLE_CAPTION_PREFIX) + 1:]).strip()
            pending_table_caption = (caption, label_match and label_match.group(1))
            position += 1
        elif line.startswith("|"):
            rows = []
            while position < len(lines) and lines[position].strip().startswith("|"):
                row_line = lines[position].strip()
                if not TABLE_DIVIDER_PATTERN.match(row_line):
                    rows.append([cell.strip() for cell in row_line.strip("|").split("|")])
                position += 1
            caption, label = pending_table_caption or ("", None)
            blocks.append(Block("table", caption, items=rows, label=label))
            pending_table_caption = None
        elif line.startswith("- "):
            items = []
            while position < len(lines) and lines[position].strip().startswith("- "):
                items.append(lines[position].strip()[2:])
                position += 1
            blocks.append(Block("bullets", items=items))
        elif NUMBERED_ITEM_PATTERN.match(line):
            items = []
            while position < len(lines) and NUMBERED_ITEM_PATTERN.match(lines[position].strip()):
                items.append(NUMBERED_ITEM_PATTERN.sub("", lines[position].strip()))
                position += 1
            blocks.append(Block("numbered", items=items))
        else:
            paragraph_lines = []
            while position < len(lines) and lines[position].strip() and not _starts_block(lines[position].strip()):
                paragraph_lines.append(lines[position].strip())
                position += 1
            blocks.append(Block("paragraph", " ".join(paragraph_lines)))
    return blocks


def _starts_block(line: str) -> bool:
    return (line.startswith(("#", "|", "- ", "![", "$$", "[[references", "[[appendix", TABLE_CAPTION_PREFIX + ":"))
            or bool(NUMBERED_ITEM_PATTERN.match(line)))


class Numbering:
    """Figure, table and citation numbers, in the order report.md first uses them."""

    def __init__(self, blocks: list[Block], source: str):
        self.labels: dict[str, int] = {}
        figure_count = table_count = 0
        for block in blocks:
            if block.kind == "figure":
                figure_count += 1
                if block.label:
                    self.labels[block.label] = figure_count
            elif block.kind == "table" and block.text:
                table_count += 1
                if block.label:
                    self.labels[block.label] = table_count
        self.citations: dict[str, int] = {}
        for key in re.findall(r"@([\w-]+)", " ".join(re.findall(r"\[@[^\]]+\]", source))):
            if key not in REFERENCES:
                raise SystemExit(f"report.md cites [@{key}], which report_references.py doesn't have")
            self.citations.setdefault(key, len(self.citations) + 1)

    def reference(self, label: str) -> str:
        if label not in self.labels:
            raise SystemExit(f"report.md refers to [[{label}]], which no figure or table has")
        prefix = FIGURE_CAPTION_PREFIX if label.startswith("fig:") else TABLE_CAPTION_PREFIX
        return f"{prefix.lower()} {self.labels[label]}"

    def citation(self, keys_text: str) -> str:
        numbers = [str(self.citations[key.strip().lstrip("@")]) for key in keys_text.split(";")]
        return "[" + ", ".join(numbers) + "]"


class ReportWriter:
    def __init__(self, numbering: Numbering):
        self._numbering = numbering
        self._document = Document()
        self._figure_number = 0
        self._table_number = 0
        self._set_up_page_and_styles()

    def _set_up_page_and_styles(self) -> None:
        section = self._document.sections[0]
        section.page_width, section.page_height = Cm(PAGE_WIDTH_CM), Cm(PAGE_HEIGHT_CM)
        for side in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
            setattr(section, side, Cm(PAGE_MARGIN_CM))
        section.different_first_page_header_footer = True  # no page number on the title page
        footer_paragraph = section.footer.paragraphs[0]
        footer_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        _add_field(footer_paragraph, "PAGE")
        for header in (section.first_page_header, section.header):
            _add_watermark(header.paragraphs[0])

        normal = self._document.styles["Normal"]
        normal.font.name = BODY_FONT
        normal.font.size = Pt(BODY_FONT_SIZE_PT)
        normal.element.rPr.rFonts.set(qn("w:eastAsia"), BODY_FONT)
        normal.paragraph_format.line_spacing = BODY_LINE_SPACING
        normal.paragraph_format.space_after = Pt(BODY_SPACE_AFTER_PT)
        for level, size in HEADING_FONT_SIZES_PT.items():
            heading = self._document.styles[f"Heading {level}"]
            heading.font.name = BODY_FONT
            heading.font.size = Pt(size)
            heading.font.bold = True
            heading_fonts = heading.element.rPr.rFonts
            for theme_attribute in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
                heading_fonts.attrib.pop(qn(theme_attribute), None)  # the theme font would override Calibri
            heading.paragraph_format.space_before = Pt(HEADING_SPACE_BEFORE_PT[level])
            heading.paragraph_format.space_after = Pt(HEADING_SPACE_AFTER_PT)
            heading.paragraph_format.keep_with_next = True

    def title_page(self) -> None:
        self._centred(UNIVERSITY_NAME, TITLE_DETAILS_FONT_SIZE_PT + 2, bold=True)
        logo_paragraph = self._document.add_paragraph()
        logo_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        logo_paragraph.add_run().add_picture(str(LOGO_IMAGE), height=Cm(LOGO_HEIGHT_CM))
        self._gap()
        self._centred(DOCUMENT_KIND, TITLE_FONT_SIZE_PT, bold=True)
        self._centred(f"по дисциплината „{COURSE_NAME}“", TITLE_DETAILS_FONT_SIZE_PT)
        self._gap()
        self._centred("Тема:", TITLE_DETAILS_FONT_SIZE_PT, bold=True)
        self._centred(TOPIC, TITLE_TOPIC_FONT_SIZE_PT, bold=True)
        self._gap()
        for label, value in (("Студент", STUDENT_NAME), ("Факултетен №", FACULTY_NUMBER), ("Група", STUDENT_GROUP)):
            paragraph = self._document.add_paragraph()
            paragraph.paragraph_format.left_indent = Cm(TEXT_WIDTH_CM / 2)
            label_run = paragraph.add_run(f"{label}: ")
            label_run.bold = True
            label_run.font.size = Pt(TITLE_DETAILS_FONT_SIZE_PT)
            paragraph.add_run(value).font.size = Pt(TITLE_DETAILS_FONT_SIZE_PT)
        self._gap()
        self._centred(f"{CITY}, {HAND_IN_DATE} г.", TITLE_DETAILS_FONT_SIZE_PT)
        self._page_break()

    def table_of_contents(self) -> None:
        self._centred(TABLE_OF_CONTENTS_HEADING, HEADING_FONT_SIZES_PT[1], bold=True)
        _add_field(self._document.add_paragraph(), f'TOC \\o "{TABLE_OF_CONTENTS_LEVELS}" \\h \\z \\u')

    def block(self, block: Block) -> None:
        getattr(self, f"_{block.kind}")(block)

    def _heading(self, block: Block) -> None:
        heading = self._document.add_heading(level=block.level)
        heading.paragraph_format.page_break_before = block.level == 1
        self._inline(heading, block.text)

    def _paragraph(self, block: Block) -> None:
        paragraph = self._document.add_paragraph()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        paragraph.paragraph_format.first_line_indent = Cm(FIRST_LINE_INDENT_CM)
        self._inline(paragraph, block.text)

    def _bullets(self, block: Block) -> None:
        for item in block.items:
            self._list_item("•", item)

    def _numbered(self, block: Block) -> None:
        for number, item in enumerate(block.items, start=1):
            self._list_item(f"{number}.", item)

    def _list_item(self, marker: str, text: str) -> None:
        paragraph = self._document.add_paragraph()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        paragraph.paragraph_format.left_indent = Cm(LIST_INDENT_CM)
        paragraph.paragraph_format.first_line_indent = Cm(-LIST_HANGING_CM)
        paragraph.paragraph_format.tab_stops.add_tab_stop(Cm(LIST_INDENT_CM))
        paragraph.add_run(f"{marker}\t")
        self._inline(paragraph, text)

    def _formula(self, block: Block) -> None:
        paragraph = self._document.add_paragraph()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = paragraph.add_run(block.text)
        run.italic = True
        run.font.name = FORMULA_FONT

    def _figure(self, block: Block) -> None:
        self._figure_number += 1
        picture_paragraph = self._document.add_paragraph()
        picture_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        picture_paragraph.paragraph_format.keep_with_next = True
        picture_path = COURSEWORK_FOLDER / block.text
        with Image.open(picture_path) as picture:
            height_per_width = picture.height / picture.width
        width_cm = min(block.width_cm or FIGURE_WIDTH_CM, FIGURE_MAX_HEIGHT_CM / height_per_width)
        picture_paragraph.add_run().add_picture(str(picture_path), width=Cm(width_cm))
        self._caption(f"{FIGURE_CAPTION_PREFIX} {self._figure_number}. ", block.items[0])

    def _table(self, block: Block) -> None:
        if block.text:
            self._table_number += 1
            caption = self._caption(f"{TABLE_CAPTION_PREFIX} {self._table_number}. ", block.text)
            caption.paragraph_format.keep_with_next = True
        rows = block.items
        column_count = len(rows[0])
        table = self._document.add_table(rows=len(rows), cols=column_count)
        table.style = "Table Grid"
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        widths = _column_widths_cm(rows)
        for row_index, row in enumerate(rows):
            for column_index in range(column_count):
                cell = table.cell(row_index, column_index)
                cell.width = Cm(widths[column_index])
                paragraph = cell.paragraphs[0]
                paragraph.paragraph_format.space_after = Pt(0)
                paragraph.paragraph_format.line_spacing = 1.0
                text = row[column_index] if column_index < len(row) else ""
                self._inline(paragraph, text, size_pt=TABLE_FONT_SIZE_PT, bold=row_index == 0)
                if row_index == 0:
                    _shade(cell, TABLE_HEADER_SHADING)
        self._document.add_paragraph()

    def _references(self, block: Block) -> None:
        for key, number in sorted(self._numbering.citations.items(), key=lambda pair: pair[1]):
            paragraph = self._document.add_paragraph()
            paragraph.paragraph_format.left_indent = Cm(REFERENCE_HANGING_CM)
            paragraph.paragraph_format.first_line_indent = Cm(-REFERENCE_HANGING_CM)
            paragraph.paragraph_format.tab_stops.add_tab_stop(Cm(REFERENCE_HANGING_CM))
            paragraph.add_run(f"[{number}]\t{REFERENCES[key]}")

    def _appendix(self, block: Block) -> None:
        appendix_number = self._last_heading_number
        files = sorted(APPENDIX_PACKAGE.glob("*.py")) + list(APPENDIX_EXTRA_FILES)
        for file_number, path in enumerate(files, start=1):
            relative_path = path.relative_to(REPO_ROOT).as_posix()
            file_title = self._document.add_paragraph()  # not a heading, so the files stay out of the contents
            file_title.paragraph_format.space_before = Pt(HEADING_SPACE_BEFORE_PT[2])
            file_title.paragraph_format.keep_with_next = True
            title_run = file_title.add_run(f"{appendix_number}.{file_number}. {relative_path}")
            title_run.bold = True
            title_run.font.name = CODE_FONT
            for code_line in path.read_text(encoding="utf-8").rstrip("\n").split("\n"):
                paragraph = self._document.add_paragraph()
                paragraph.paragraph_format.space_after = Pt(0)
                paragraph.paragraph_format.line_spacing = 1.0
                run = paragraph.add_run(code_line.rstrip() or " ")
                run.font.name = CODE_FONT
                run.font.size = Pt(CODE_FONT_SIZE_PT)

    @property
    def _last_heading_number(self) -> str:
        level_one = [paragraph.text for paragraph in self._document.paragraphs if paragraph.style.name == "Heading 1"]
        return HEADING_NUMBER_PATTERN.match(level_one[-1]).group(1)

    def _caption(self, prefix: str, text: str):
        paragraph = self._document.add_paragraph()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        prefix_run = paragraph.add_run(prefix)
        prefix_run.bold = True
        prefix_run.font.size = Pt(CAPTION_FONT_SIZE_PT)
        self._inline(paragraph, text, size_pt=CAPTION_FONT_SIZE_PT, italic=True)
        return paragraph

    def _inline(self, paragraph, text: str, size_pt: float | None = None, bold: bool = False,
                italic: bool = False) -> None:
        """text, with its inline marks, appended to the paragraph as runs."""
        text = text.replace("\\_", "_")
        for piece in INLINE_PATTERN.split(text):
            if not piece:
                continue
            run_bold, run_italic, code, highlight = bold, italic, False, False
            if piece.startswith("**"):
                piece, run_bold = piece[2:-2], True
            elif piece.startswith("`"):
                piece, code = piece[1:-1], True
            elif piece.startswith("=="):
                piece, highlight = piece[2:-2], True
            elif piece.startswith("[@"):
                piece = self._numbering.citation(piece[1:-1])
            elif piece.startswith("[["):
                piece = self._numbering.reference(piece[2:-2])
            elif piece.startswith("*") and piece.endswith("*") and len(piece) > 2:
                piece, run_italic = piece[1:-1], True
            run = paragraph.add_run(piece)
            run.bold = run_bold or None
            run.italic = run_italic or None
            if size_pt:
                run.font.size = Pt(size_pt)
            if code:
                run.font.name = CODE_FONT
                run.font.size = Pt(min(size_pt or INLINE_CODE_FONT_SIZE_PT, INLINE_CODE_FONT_SIZE_PT))
            if highlight:
                run.font.highlight_color = getattr(WD_COLOR_INDEX, PLACEHOLDER_HIGHLIGHT)

    def _centred(self, text: str, size_pt: float, bold: bool = False) -> None:
        paragraph = self._document.add_paragraph()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = paragraph.add_run(text)
        run.bold = bold
        run.font.size = Pt(size_pt)

    def _gap(self) -> None:
        for _ in range(TITLE_GAP_LINES):
            self._document.add_paragraph()

    def _page_break(self) -> None:
        self._document.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    def save(self) -> None:
        self._document.save(str(REPORT_OUTPUT))


def _column_widths_cm(rows: list[list[str]]) -> list[float]:
    """Each column's width, shared out by the length of its longest cell."""
    weights = []
    for column_index in range(len(rows[0])):
        longest = max(len(row[column_index]) if column_index < len(row) else 0 for row in rows)
        weights.append(min(max(longest, TABLE_COLUMN_MINIMUM_WEIGHT), TABLE_COLUMN_MAXIMUM_WEIGHT))
    return [TEXT_WIDTH_CM * weight / sum(weights) for weight in weights]


def _add_field(paragraph, instruction: str) -> None:
    """A Word field (PAGE, TOC...), left for Word to fill in."""
    run = paragraph.add_run()
    for kind, text in (("begin", None), (None, instruction), ("separate", None), ("end", None)):
        if kind:
            element = OxmlElement("w:fldChar")
            element.set(qn("w:fldCharType"), kind)
        else:
            element = OxmlElement("w:instrText")
            element.set(qn("xml:space"), "preserve")
            element.text = text
        run._r.append(element)


def _add_watermark(header_paragraph) -> None:
    """The faded logo, floating behind the text in the middle of every page the header is on.
    python-docx only places pictures in line, so the inline picture is turned into an anchored one."""
    logo = Image.open(WATERMARK_IMAGE).convert("RGBA")
    logo.putalpha(logo.getchannel("A").point(lambda alpha: round(alpha * WATERMARK_OPACITY)))
    faded_logo = io.BytesIO()
    logo.save(faded_logo, format="PNG")
    inline = header_paragraph.add_run().add_picture(faded_logo, width=Cm(WATERMARK_WIDTH_CM))._inline

    anchor = OxmlElement("wp:anchor")
    for attribute, value in (("distT", "0"), ("distB", "0"), ("distL", "0"), ("distR", "0"), ("simplePos", "0"),
                             ("relativeHeight", "0"), ("behindDoc", "1"), ("locked", "0"), ("layoutInCell", "1"),
                             ("allowOverlap", "1")):
        anchor.set(attribute, value)
    simple_position = OxmlElement("wp:simplePos")
    simple_position.set("x", "0")
    simple_position.set("y", "0")
    anchor.append(simple_position)
    for axis in ("wp:positionH", "wp:positionV"):
        position = OxmlElement(axis)
        position.set("relativeFrom", "page")
        alignment = OxmlElement("wp:align")
        alignment.text = "center"
        position.append(alignment)
        anchor.append(position)
    anchor.append(inline.find(qn("wp:extent")))
    effect_extent = OxmlElement("wp:effectExtent")
    for side in ("l", "t", "r", "b"):
        effect_extent.set(side, "0")
    anchor.append(effect_extent)
    anchor.append(OxmlElement("wp:wrapNone"))
    for child_name in ("wp:docPr", "wp:cNvGraphicFramePr", "a:graphic"):
        anchor.append(inline.find(qn(child_name)))
    inline.getparent().replace(inline, anchor)


def _shade(cell, colour: str) -> None:
    shading = OxmlElement("w:shd")
    shading.set(qn("w:val"), "clear")
    shading.set(qn("w:color"), "auto")
    shading.set(qn("w:fill"), colour)
    cell._tc.get_or_add_tcPr().append(shading)


WORD_UPDATE_SCRIPT = """
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {{
    $document = $word.Documents.Open('{docx}')
    $document.TablesOfContents | ForEach-Object {{ $_.Update() }}
    $document.Fields.Update() | Out-Null
    $document.Save()
    if ('{pdf}') {{ $document.ExportAsFixedFormat('{pdf}', {pdf_format}) }}
    $document.Close()
}} finally {{ $word.Quit() }}
"""


def update_with_word(pdf_path: str | None) -> bool:
    """Has Word fill in the table of contents and page fields (and export a PDF); False if Word isn't there."""
    if sys.platform != "win32":
        return False
    script = WORD_UPDATE_SCRIPT.format(docx=REPORT_OUTPUT, pdf=pdf_path or "", pdf_format=WORD_PDF_FORMAT)
    finished = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
                              capture_output=True, text=True)
    return finished.returncode == 0 and not finished.stderr.strip()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--pdf", help="also export a PDF to this path (needs Word)")
    arguments = parser.parse_args()

    source = REPORT_SOURCE.read_text(encoding="utf-8")
    blocks = parse_markdown(source)
    writer = ReportWriter(Numbering(blocks, source))
    writer.title_page()
    writer.table_of_contents()
    for block in blocks:
        writer.block(block)
    writer.save()
    if update_with_word(arguments.pdf):
        print(f"Wrote {REPORT_OUTPUT} (table of contents filled in by Word)")
    else:
        print(f"Wrote {REPORT_OUTPUT}; open it in Word and press F9 on the table of contents to fill it in")


if __name__ == "__main__":
    main()
