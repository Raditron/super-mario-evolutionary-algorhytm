"""Test levels and stepping helpers shared by the game tests."""

from mario.constants.level import LEVEL_HEIGHT_TILES
from mario.controller.controller_state import ControllerState
from mario.level.static_level import StaticLevel
from mario.simulation.mario import Mario

GROUND_TOP_ROW = 13
TEST_LEVEL_WIDTH_TILES = 120

HOLD_NOTHING = ControllerState.bitmask()
HOLD_RIGHT = ControllerState.bitmask(right=True)
HOLD_LEFT = ControllerState.bitmask(left=True)
HOLD_RIGHT_RUN = ControllerState.bitmask(right=True, run=True)
HOLD_JUMP = ControllerState.bitmask(jump=True)


def build_level(pit_columns: range = range(0), hard_blocks: frozenset[tuple[int, int]] = frozenset(),
                width_tiles: int = TEST_LEVEL_WIDTH_TILES) -> StaticLevel:
    """Open sky over two rows of ground, with an optional pit and hard blocks at (column, row)."""
    rows = []
    for row in range(LEVEL_HEIGHT_TILES):
        characters = []
        for column in range(width_tiles):
            if (column, row) in hard_blocks:
                characters.append("#")
            elif row >= GROUND_TOP_ROW and column not in pit_columns:
                characters.append("X")
            else:
                characters.append(".")
        rows.append("".join(characters))
    return StaticLevel(rows)


def step_mario(mario: Mario, level: StaticLevel, buttons: int, ticks: int = 1) -> None:
    controller = ControllerState(buttons)
    for _ in range(ticks):
        mario.step(controller, level)
