"""One Attempt's blocks: what a hit from below does to each (the original's
PlayerHeadCollision, BumpBlock and BrickShatter; docs/research/smb-physics-constants.md,
"Added during the build (#18)" and "(#19)", and docs/research/world-1-1-layout.md).

Big Mario breaks a plain brick, which leaves an empty tile; everything else,
and every block small Mario hits, is bumped. A power-up ? block releases a
Super Mushroom, and the hidden block a 1-UP mushroom (BumpBlock, SetupPowerUp).
An enemy standing on a block while it bounces, or on a brick as it breaks, is
defeated (HandleEToBGCollision); an item there hops away from Mario. The multi-coin brick's timer is one for the
whole level, as in the original (BrickCoinTimerFlag); 1-1 has one such brick.
"""

from enum import Enum, auto

from mario.constants.level import TILE_SIZE_SUBPIXELS
from mario.constants.physics import BLOCK_BOUNCE_LOCKOUT_TICKS, MULTI_COIN_BRICK_TICKS
from mario.constants.scoring import BROKEN_BRICK_POINTS, BUMPED_ENEMY_POINTS
from mario.level.tile_kind import BLOCK_TILE_KINDS, TileKind
from mario.simulation.attempt_result import DefeatMethod, GameEvent, GameEventKind
from mario.simulation.attempt_tiles import AttemptTiles
from mario.simulation.bouncing_block import BouncingBlock
from mario.simulation.enemy import Enemy
from mario.simulation.item_kind import ItemKind
from mario.simulation.items import Items
from mario.simulation.mushroom import Mushroom
from mario.simulation.scoreboard import Scoreboard
from mario.simulation.walking_body import WalkingBody


class HeadHit(Enum):
    """What Mario's head did to the tile it hit from below."""
    NOTHING = auto()
    BUMPED_BLOCK = auto()
    BROKE_BRICK = auto()


class Blocks:
    def __init__(self, tiles: AttemptTiles, scoreboard: Scoreboard, items: Items, events: list[GameEvent]):
        self._tiles = tiles
        self._items = items
        self._scoreboard = scoreboard
        self._events = events
        self._multi_coin_ticks_left: int | None = None             # None until the first hit
        self._bounce_lockout_ticks_left = 0
        self.bouncing: list[BouncingBlock] = []
        self._broken_this_tick: list[tuple[int, int]] = []

    def hit_from_below(self, column: int, row: int, tick: int, breaks_bricks: bool) -> HeadHit:
        """Mario's head hit this tile from below; breaks_bricks when he is big."""
        kind = self._tiles.tile_kind(column, row)
        if kind not in BLOCK_TILE_KINDS or self._bounce_lockout_ticks_left > 0:
            return HeadHit.NOTHING
        self._bounce_lockout_ticks_left = BLOCK_BOUNCE_LOCKOUT_TICKS
        if kind is TileKind.BRICK and breaks_bricks:
            self._break_brick(column, row, tick)
            return HeadHit.BROKE_BRICK
        self.bouncing.append(BouncingBlock(column, row))
        if kind is TileKind.COIN_QUESTION_BLOCK:
            self._events.append(GameEvent(tick, GameEventKind.HIT_QUESTION_BLOCK))
            self._scoreboard.collect_coin(tick)
            self._tiles.change_block(column, row, TileKind.USED_BLOCK)
        elif kind is TileKind.POWER_UP_QUESTION_BLOCK:
            self._events.append(GameEvent(tick, GameEventKind.HIT_QUESTION_BLOCK))
            self._tiles.change_block(column, row, TileKind.USED_BLOCK)
            # Big Mario gets a fire flower in the original; until it is built, a mushroom.
            self._items.release(ItemKind.SUPER_MUSHROOM, column, row)
        elif kind is TileKind.STARMAN_BRICK:
            self._tiles.change_block(column, row, TileKind.USED_BLOCK)
        elif kind is TileKind.MULTI_COIN_BRICK:
            self._hit_multi_coin_brick(column, row, tick)
        elif kind is TileKind.HIDDEN_ONE_UP_BLOCK:
            self._events.append(GameEvent(tick, GameEventKind.HIT_HIDDEN_BLOCK))
            self._tiles.change_block(column, row, TileKind.USED_BLOCK)
            self._items.release(ItemKind.ONE_UP_MUSHROOM, column, row)
        return HeadHit.BUMPED_BLOCK

    def defeat_enemies_on_bumped_blocks(self, enemies: list[Enemy], mario_x: int, tick: int) -> None:
        """Defeat each enemy standing on a bouncing block, or on a brick broken this tick."""
        for enemy in enemies:
            if not enemy.is_defeated and self._is_on_a_bumped_block(enemy):
                enemy.defeat_by_bump(mario_x)
                self._events.append(GameEvent(tick, GameEventKind.DEFEATED_ENEMY, DefeatMethod.BUMPED))
                self._scoreboard.score_points(BUMPED_ENEMY_POINTS, tick)

    def knock_items_on_bumped_blocks(self, items: list[Mushroom], mario_x: int) -> None:
        """An item standing on a bouncing block, or on a brick broken this tick,
        hops away from Mario. One still rising out of its block stands on nothing."""
        for item in items:
            if not item.is_emerging and self._is_on_a_bumped_block(item):
                item.hop_away_from(mario_x)

    def step(self) -> None:
        """One tick passes: bumped blocks bounce, and timers count down."""
        for block in self.bouncing:
            block.step()
        self.bouncing = [block for block in self.bouncing if not block.is_back_in_place]
        self._broken_this_tick = []
        if self._multi_coin_ticks_left:
            self._multi_coin_ticks_left -= 1
        if self._bounce_lockout_ticks_left > 0:
            self._bounce_lockout_ticks_left -= 1

    def _break_brick(self, column: int, row: int, tick: int) -> None:
        self._tiles.change_block(column, row, TileKind.EMPTY)
        self._broken_this_tick.append((column, row))
        self._events.append(GameEvent(tick, GameEventKind.BROKE_BRICK))
        self._scoreboard.score_points(BROKEN_BRICK_POINTS, tick)

    def _hit_multi_coin_brick(self, column: int, row: int, tick: int) -> None:
        if self._multi_coin_ticks_left is None:
            self._multi_coin_ticks_left = MULTI_COIN_BRICK_TICKS
        elif self._multi_coin_ticks_left == 0:
            self._tiles.change_block(column, row, TileKind.USED_BLOCK)
        self._scoreboard.collect_coin(tick)

    def _is_on_a_bumped_block(self, body: WalkingBody) -> bool:
        """A broken brick's tile is already empty when enemies and items move, so
        one that stood on it has just started to fall but not yet moved."""
        return (any(not body.is_falling and _is_on_top_of(body, block.column, block.row)
                    for block in self.bouncing)
                or any(_is_on_top_of(body, column, row) for column, row in self._broken_this_tick))


def _is_on_top_of(body: WalkingBody, column: int, row: int) -> bool:
    """Its centre is over the tile and its feet are on top of it (the original's
    foot probe is at its bottom middle)."""
    return body.centre_column == column and body.feet_y == row * TILE_SIZE_SUBPIXELS
