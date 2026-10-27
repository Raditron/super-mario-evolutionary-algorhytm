"""One Attempt's blocks: what a hit from below does to each (the original's
PlayerHeadCollision and BumpBlock; docs/research/smb-physics-constants.md,
"Added during the build (#18)", and docs/research/world-1-1-layout.md).

An enemy standing on a block while it bounces is defeated (HandleEToBGCollision).
The multi-coin brick's timer is one for the whole level, as in the original
(BrickCoinTimerFlag); 1-1 has one such brick.
"""

from mario.constants.level import TILE_SIZE_SUBPIXELS
from mario.constants.physics import BLOCK_BOUNCE_LOCKOUT_TICKS, MULTI_COIN_BRICK_TICKS
from mario.constants.scoring import BUMPED_ENEMY_POINTS
from mario.level.tile_kind import BLOCK_TILE_KINDS, TileKind
from mario.simulation.attempt_result import DefeatMethod, GameEvent, GameEventKind
from mario.simulation.attempt_tiles import AttemptTiles
from mario.simulation.bouncing_block import BouncingBlock
from mario.simulation.enemy import Enemy
from mario.simulation.scoreboard import Scoreboard


class Blocks:
    def __init__(self, tiles: AttemptTiles, scoreboard: Scoreboard, events: list[GameEvent]):
        self._tiles = tiles
        self._scoreboard = scoreboard
        self._events = events
        self._multi_coin_ticks_left: int | None = None             # None until the first hit
        self._bounce_lockout_ticks_left = 0
        self.bouncing: list[BouncingBlock] = []

    def hit_from_below(self, column: int, row: int, tick: int) -> bool:
        """Mario's head hit this tile from below. True if it bumped a block; small
        Mario only bumps a plain brick."""
        kind = self._tiles.tile_kind(column, row)
        if kind not in BLOCK_TILE_KINDS or self._bounce_lockout_ticks_left > 0:
            return False
        self._bounce_lockout_ticks_left = BLOCK_BOUNCE_LOCKOUT_TICKS
        self.bouncing.append(BouncingBlock(column, row))
        if kind is TileKind.COIN_QUESTION_BLOCK:
            self._events.append(GameEvent(tick, GameEventKind.HIT_QUESTION_BLOCK))
            self._scoreboard.collect_coin(tick)
            self._tiles.change_block(column, row, TileKind.USED_BLOCK)
        elif kind is TileKind.POWER_UP_QUESTION_BLOCK:
            self._events.append(GameEvent(tick, GameEventKind.HIT_QUESTION_BLOCK))
            self._tiles.change_block(column, row, TileKind.USED_BLOCK)
        elif kind is TileKind.STARMAN_BRICK:
            self._tiles.change_block(column, row, TileKind.USED_BLOCK)
        elif kind is TileKind.MULTI_COIN_BRICK:
            self._hit_multi_coin_brick(column, row, tick)
        elif kind is TileKind.HIDDEN_ONE_UP_BLOCK:
            self._events.append(GameEvent(tick, GameEventKind.HIT_HIDDEN_BLOCK))
            self._tiles.change_block(column, row, TileKind.USED_BLOCK)
        return True

    def defeat_enemies_on_bouncing_blocks(self, enemies: list[Enemy], mario_x: int, tick: int) -> None:
        for enemy in enemies:
            if not enemy.is_defeated and any(_is_standing_on(enemy, block) for block in self.bouncing):
                enemy.defeat_by_bump(mario_x)
                self._events.append(GameEvent(tick, GameEventKind.DEFEATED_ENEMY, DefeatMethod.BUMPED))
                self._scoreboard.score_points(BUMPED_ENEMY_POINTS, tick)

    def step(self) -> None:
        """One tick passes: bumped blocks bounce, and timers count down."""
        for block in self.bouncing:
            block.step()
        self.bouncing = [block for block in self.bouncing if not block.is_back_in_place]
        if self._multi_coin_ticks_left:
            self._multi_coin_ticks_left -= 1
        if self._bounce_lockout_ticks_left > 0:
            self._bounce_lockout_ticks_left -= 1

    def _hit_multi_coin_brick(self, column: int, row: int, tick: int) -> None:
        if self._multi_coin_ticks_left is None:
            self._multi_coin_ticks_left = MULTI_COIN_BRICK_TICKS
        elif self._multi_coin_ticks_left == 0:
            self._tiles.change_block(column, row, TileKind.USED_BLOCK)
        self._scoreboard.collect_coin(tick)


def _is_standing_on(enemy: Enemy, block: BouncingBlock) -> bool:
    """Its centre is over the block and its feet are on top of it (the original's
    foot probe is at its bottom middle)."""
    return (not enemy.is_falling and enemy.centre_column == block.column
            and enemy.feet_y == block.row * TILE_SIZE_SUBPIXELS)
