"""Reading World 1-1's data file, mario/level/world_1_1.toml."""

import tomllib
from pathlib import Path

from mario.constants.level import LEVEL_FILE_NAME, LEVEL_HEIGHT_TILES, LEVEL_WIDTH_TILES


def read_level_data() -> dict:
    return tomllib.loads(Path(__file__).with_name(LEVEL_FILE_NAME).read_text())


def grid_layer_rows(level_data: dict, layer_name: str) -> list[str]:
    """One of the file's grid layers, row by row from the top, one character per tile."""
    rows = level_data[layer_name].split()
    if len(rows) != LEVEL_HEIGHT_TILES or any(len(row) != LEVEL_WIDTH_TILES for row in rows):
        raise ValueError(f"{LEVEL_FILE_NAME}: {layer_name} must be "
                         f"{LEVEL_WIDTH_TILES} x {LEVEL_HEIGHT_TILES} tiles")
    return rows
