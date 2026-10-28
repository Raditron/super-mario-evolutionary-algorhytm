"""The shared, read-only World 1-1: the tile grid plus its block, pipe and enemy tables.

One StaticLevel is loaded per process and shared by every Attempt; nothing
ever writes to it.
"""

from dataclasses import dataclass
from enum import StrEnum

from mario.constants.level import (
    GOOMBA_PAIR_FIRST_OFFSET_PIXELS,
    GOOMBA_PAIR_SECOND_OFFSET_PIXELS,
    TILE_SIZE_PIXELS,
)
from mario.level.level_file import grid_layer_rows, read_level_data
from mario.level.tile_kind import BLOCK_TILE_KINDS, SOLID_TILE_KINDS, TILE_KIND_BY_CHARACTER, TileKind


# The level data's grid layer with the solid and interactive tiles.
LAYER_NAME = "layer_1"
# An enemies entry of this kind places two Goombas relative to its data column.
GOOMBA_PAIR_ENTRY_KIND = "goomba_pair"


class PipeDestination(StrEnum):
    NOTHING = "nothing"
    BONUS_ROOM = "bonus_room"
    BONUS_ROOM_EXIT = "bonus_room_exit"


class EnemyKind(StrEnum):
    GOOMBA = "goomba"
    KOOPA = "koopa"


@dataclass(frozen=True)
class Block:
    column: int
    row: int
    kind: TileKind


@dataclass(frozen=True)
class Pipe:
    left_column: int
    top_row: int
    height_tiles: int
    leads_to: PipeDestination


@dataclass(frozen=True)
class EnemySpawn:
    """Where an enemy starts: its x, the row of the tile it rests on, and the x
    whose coming into range activates it (a Goomba pair's data column, otherwise
    its own x)."""
    kind: EnemyKind
    x_pixels: int
    resting_row: int
    activation_x_pixels: int


class StaticLevel:
    """Tile lookup and the level's tables. Columns and rows outside the grid
    are solid at the sides and open above and below (pits). flagpole_column is the
    column of the flagpole, None in a level without one."""

    def __init__(self, layer_1_rows: list[str], pipes: tuple[Pipe, ...] = (),
                 enemy_spawns: tuple[EnemySpawn, ...] = ()):
        self.width_tiles = len(layer_1_rows[0])
        self.height_tiles = len(layer_1_rows)
        self._tile_rows = tuple(tuple(TILE_KIND_BY_CHARACTER[character] for character in row)
                                for row in layer_1_rows)
        # bytearrays: the fastest per-tile lookup from plain Python, for the hot path.
        # Each Attempt copies them (AttemptTiles); nothing writes to these.
        self.solid_rows = tuple(bytearray(kind in SOLID_TILE_KINDS for kind in row)
                                 for row in self._tile_rows)
        self.blocks = tuple(Block(column, row, kind)
                            for row, kinds in enumerate(self._tile_rows)
                            for column, kind in enumerate(kinds) if kind in BLOCK_TILE_KINDS)
        self.pipes = pipes
        self.enemy_spawns = enemy_spawns
        self.flagpole_column = next((column for column in range(self.width_tiles)
                                     if any(kinds[column] is TileKind.FLAGPOLE for kinds in self._tile_rows)),
                                    None)

    @classmethod
    def load_world_1_1(cls) -> "StaticLevel":
        level_data = read_level_data()
        layer_1_rows = grid_layer_rows(level_data, LAYER_NAME)
        pipes = tuple(Pipe(entry["left_column"], entry["top_row"], entry["height_tiles"],
                           PipeDestination(entry["leads_to"]))
                      for entry in level_data["pipes"])
        enemy_spawns = tuple(spawn for entry in level_data["enemies"]
                             for spawn in _enemy_spawns_from_entry(entry))
        return cls(layer_1_rows, pipes, enemy_spawns)

    def tile_kind(self, column: int, row: int) -> TileKind:
        if row < 0 or row >= self.height_tiles:
            return TileKind.EMPTY
        if column < 0 or column >= self.width_tiles:
            return TileKind.HARD_BLOCK
        return self._tile_rows[row][column]

    def is_solid(self, column: int, row: int) -> bool:
        if row < 0 or row >= self.height_tiles:
            return False
        if column < 0 or column >= self.width_tiles:
            return True
        return self.solid_rows[row][column] == 1


def _enemy_spawns_from_entry(entry: dict) -> tuple[EnemySpawn, ...]:
    data_x_pixels = entry["data_column"] * TILE_SIZE_PIXELS
    resting_row = entry["resting_row"]
    if entry["kind"] == GOOMBA_PAIR_ENTRY_KIND:
        # The original places a pair when its data column comes into range (HandleGroupEnemies).
        return (EnemySpawn(EnemyKind.GOOMBA, data_x_pixels + GOOMBA_PAIR_FIRST_OFFSET_PIXELS, resting_row,
                           data_x_pixels),
                EnemySpawn(EnemyKind.GOOMBA, data_x_pixels + GOOMBA_PAIR_SECOND_OFFSET_PIXELS, resting_row,
                           data_x_pixels))
    return (EnemySpawn(EnemyKind(entry["kind"]), data_x_pixels, resting_row, data_x_pixels),)
