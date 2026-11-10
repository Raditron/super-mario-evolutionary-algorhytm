"""Test levels and stepping helpers shared by the game tests."""

import copy

from mario.constants.level import LEVEL_HEIGHT_TILES, TILE_SIZE_PIXELS
from mario.controller.controller_state import ControllerState
from mario.level.static_level import EnemyKind, EnemySpawn, Pipe, StaticLevel
from mario.simulation.attempt import Attempt
from mario.simulation.attempt_tiles import AttemptTiles
from mario.simulation.mario import Mario

GROUND_TOP_ROW = 13
TEST_LEVEL_WIDTH_TILES = 120
# World 1-1's castle stopper column: the castle walk ends with Mario's right edge at its left edge.
CASTLE_STOPPER_COLUMN = 205
CASTLE_STOPPER_X_PIXELS = CASTLE_STOPPER_COLUMN * TILE_SIZE_PIXELS
# Jumping at enemies too, the scripted pilot reaches 1-1's flagpole, touching it in mid-air well above its foot.
PILOT_ENEMY_LOOK_AHEAD_PIXELS = 40

HOLD_NOTHING = ControllerState.bitmask()
HOLD_RIGHT = ControllerState.bitmask(right=True)
HOLD_LEFT = ControllerState.bitmask(left=True)
HOLD_RIGHT_RUN = ControllerState.bitmask(right=True, run=True)
HOLD_JUMP = ControllerState.bitmask(jump=True)
HOLD_DOWN = ControllerState.bitmask(down=True)
HOLD_RIGHT_JUMP = ControllerState.bitmask(right=True, jump=True)

PIPE_WIDTH_PIXELS = 2 * TILE_SIZE_PIXELS
# Walking right from 1-1's start and jumping at a wall this close ahead, Mario lands on the warp pipe.
PIPE_PILOT_WALL_LOOK_AHEAD_PIXELS = 40
# Standing on the warp pipe with his box's left edge here, both of Mario's foot
# probes (sprite x + 3 and + 12) are on its top: sprite x 916 to 924.
WARP_PIPE_ENTRY_HITBOX_X_PIXELS = range(918, 927)
# ChangeAreaTimer = $30: Mario sinks 1 px a tick for 48 ticks, then the area changes.
SINKING_TICKS = 48


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
    while attempt.mario.is_changing_power_state:
        attempt.step(HOLD_NOTHING)
    return attempt


def fire_mario_attempt(level: StaticLevel, **attempt_options) -> Attempt:
    """An Attempt whose Mario grew and then caught fire at the start, as a fire
    flower makes him, and has finished catching fire (tests/game/test_fire_flower.py
    collects a real one)."""
    attempt = big_mario_attempt(level, **attempt_options)
    attempt.mario.power_up()
    while attempt.mario.is_changing_power_state:
        attempt.step(HOLD_NOTHING)
    return attempt


def walk_onto_the_warp_pipe(attempt: Attempt, hitbox_x_pixels: int = WARP_PIPE_ENTRY_HITBOX_X_PIXELS.start) -> None:
    """From 1-1's start (best without enemies), walk right, jumping at walls, until
    Mario stands on the warp pipe's top; then step him along it until he stands
    still with his box's left edge here."""
    walk_onto_pipe(attempt, attempt.level.warp_pipe, hitbox_x_pixels)


def in_the_bonus_room(level: StaticLevel, **attempt_options) -> Attempt:
    """An attempt in 1-1 (best without enemies) whose Mario has just arrived in the
    bonus room: down on the warp pipe, then the sinking; his drop into the room is to come."""
    attempt = Attempt(level, **attempt_options)
    walk_onto_the_warp_pipe(attempt)
    for _ in range(1 + SINKING_TICKS):
        attempt.step(HOLD_DOWN)
    return attempt


def walk_onto_pipe(attempt: Attempt, pipe: Pipe, hitbox_x_pixels: int) -> None:
    """walk_onto_the_warp_pipe, onto the given pipe."""
    jump_held_last_tick = False
    while not _stands_on_top_of(attempt.mario, pipe):
        if attempt.mario.is_on_ground:
            jump = not jump_held_last_tick and _wall_ahead(attempt)
        else:
            jump = jump_held_last_tick
        jump_held_last_tick = jump
        attempt.step(HOLD_RIGHT_JUMP if jump else HOLD_RIGHT)
    while attempt.mario.pixel_x != hitbox_x_pixels or attempt.mario.whole_speed_x != 0:
        if attempt.mario.pixel_x < hitbox_x_pixels:
            attempt.step(HOLD_RIGHT)
        elif attempt.mario.pixel_x > hitbox_x_pixels:
            attempt.step(HOLD_LEFT)
        else:
            attempt.step(HOLD_NOTHING)


def _stands_on_top_of(mario: Mario, pipe: Pipe) -> bool:
    pipe_left_x_pixels = pipe.left_column * TILE_SIZE_PIXELS
    return (mario.is_on_ground and mario.hitbox().bottom_y_pixels == pipe.top_row * TILE_SIZE_PIXELS
            and pipe_left_x_pixels <= mario.pixel_x < pipe_left_x_pixels + PIPE_WIDTH_PIXELS)


def _wall_ahead(attempt: Attempt) -> bool:
    hitbox = attempt.mario.hitbox()
    rows = range(hitbox.y_pixels // TILE_SIZE_PIXELS, (hitbox.bottom_y_pixels - 1) // TILE_SIZE_PIXELS + 1)
    columns = range(hitbox.right_x_pixels // TILE_SIZE_PIXELS,
                    (hitbox.right_x_pixels + PIPE_PILOT_WALL_LOOK_AHEAD_PIXELS) // TILE_SIZE_PIXELS + 1)
    return any(attempt.tiles.is_solid(column, row) for column in columns for row in rows)


def step_mario(mario: Mario, level: StaticLevel, buttons: int, ticks: int = 1) -> None:
    """Step Mario alone in the level, with no blocks to change."""
    controller = ControllerState(buttons)
    tiles = AttemptTiles(level)
    for _ in range(ticks):
        mario.step(controller, tiles)
