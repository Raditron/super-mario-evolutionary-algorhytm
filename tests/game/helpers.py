"""Test levels and stepping helpers shared by the game tests."""

import copy

from mario.constants.level import LEVEL_HEIGHT_TILES
from mario.controller.controller_state import ControllerState
from mario.level.static_level import EnemyKind, EnemySpawn, StaticLevel
from mario.simulation.attempt import Attempt
from mario.simulation.attempt_tiles import AttemptTiles
from mario.simulation.mario import Mario

GROUND_TOP_ROW = 13
TEST_LEVEL_WIDTH_TILES = 120

HOLD_NOTHING = ControllerState.bitmask()
HOLD_RIGHT = ControllerState.bitmask(right=True)
HOLD_LEFT = ControllerState.bitmask(left=True)
HOLD_RIGHT_RUN = ControllerState.bitmask(right=True, run=True)
HOLD_JUMP = ControllerState.bitmask(jump=True)


def build_level(pit_columns: range = range(0), hard_blocks: frozenset[tuple[int, int]] = frozenset(),
                width_tiles: int = TEST_LEVEL_WIDTH_TILES,
                enemy_spawns: tuple[EnemySpawn, ...] = (),
                blocks: dict[tuple[int, int], str] | None = None) -> StaticLevel:
    """Open sky over two rows of ground, with an optional pit, hard blocks at
    (column, row), other tiles by their level-data character, and enemies."""
    blocks = blocks or {}
    rows = []
    for row in range(LEVEL_HEIGHT_TILES):
        characters = []
        for column in range(width_tiles):
            if (column, row) in blocks:
                characters.append(blocks[column, row])
            elif (column, row) in hard_blocks:
                characters.append("#")
            elif row >= GROUND_TOP_ROW and column not in pit_columns:
                characters.append("X")
            else:
                characters.append(".")
        rows.append("".join(characters))
    return StaticLevel(rows, enemy_spawns=enemy_spawns)


def goomba_spawn(x_pixels: int, resting_row: int = GROUND_TOP_ROW - 1) -> EnemySpawn:
    """A Goomba resting on the ground (or on the given row), starting at x."""
    return EnemySpawn(EnemyKind.GOOMBA, x_pixels, resting_row, x_pixels)


def without_enemies(level: StaticLevel) -> StaticLevel:
    """The same level with an empty enemy table."""
    level_without_enemies = copy.copy(level)
    level_without_enemies.enemy_spawns = ()
    return level_without_enemies


def big_mario_attempt(level: StaticLevel, **attempt_options) -> Attempt:
    """An Attempt whose Mario grew at the start, as a Super Mushroom makes him, and
    has finished growing (tests/game/test_power_ups.py collects a real one)."""
    attempt = Attempt(level, **attempt_options)
    attempt.mario.grow()
    while attempt.mario.is_changing_size:
        attempt.step(HOLD_NOTHING)
    return attempt


def step_mario(mario: Mario, level: StaticLevel, buttons: int, ticks: int = 1) -> None:
    """Step Mario alone in the level, with no blocks to change."""
    controller = ControllerState(buttons)
    tiles = AttemptTiles(level)
    for _ in range(ticks):
        mario.step(controller, tiles)
