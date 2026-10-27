"""One Attempt: one life of one Mario in a freshly loaded level.

Its only way in is step(buttons), one tick given that tick's Controller
bitmask. It uses no randomness, no floats and no wall clock, so the same
Controller log always gives the same Attempt.

It ends when Mario dies or the level timer runs out, and, if the mode turns
the stall rule on (training does, play doesn't), when he stalls. While Mario
grows, shrinks or catches fire, everything else stands still, the level timer
too; the ticks still count, and so does the stall rule.
"""

from mario.constants.level import CHECKPOINT_LEFT_X_PIXELS
from mario.constants.scoring import ITEM_POINTS
from mario.controller.controller_state import ControllerState
from mario.level.static_level import StaticLevel
from mario.simulation.attempt_result import AttemptResult, DefeatMethod, EndReason, GameEvent, GameEventKind
from mario.simulation.attempt_tiles import AttemptTiles
from mario.simulation.blocks import Blocks, HeadHit
from mario.simulation.enemy_collision_check import EnemyCollisionCheck, EnemyCollisionOutcome, is_enemy_check_tick
from mario.simulation.enemy_roster import EnemyRoster
from mario.simulation.fireballs import Fireballs
from mario.simulation.items import Items
from mario.simulation.level_timer import LevelTimer
from mario.simulation.mario import Mario
from mario.simulation.playfield import Playfield
from mario.simulation.item_kind import ItemKind
from mario.simulation.item import Item
from mario.simulation.scoreboard import Scoreboard
from mario.simulation.scroll import Scroll
from mario.simulation.stall_rule import StallRule


class Attempt:
    def __init__(self, level: StaticLevel, *, ends_on_stall: bool = False, from_checkpoint: bool = False):
        """ends_on_stall turns the stall rule on. from_checkpoint starts Mario
        with the screen's left edge at the checkpoint (play mode only)."""
        screen_left_x_pixels = CHECKPOINT_LEFT_X_PIXELS if from_checkpoint else 0
        self.level = level
        self.tiles = AttemptTiles(level)
        self.mario = Mario(screen_left_x_pixels)
        self.scroll = Scroll(self.mario.pixel_x, screen_left_x_pixels)
        self._playfield = Playfield(self.tiles, self.scroll)
        self.enemies = EnemyRoster(level.enemy_spawns)
        self.items = Items()
        self._enemy_collision_check = EnemyCollisionCheck()
        self._died_to_enemy = False
        self.level_timer = LevelTimer()
        self.ticks_elapsed = 0
        self.furthest_x = self.mario.pixel_x
        self.events: list[GameEvent] = []
        self.scoreboard = Scoreboard(self.events)
        self.blocks = Blocks(self.tiles, self.scoreboard, self.items, self.events)
        self.fireballs = Fireballs(self.mario, self.scoreboard, self.events)
        self._stall_rule = StallRule(self.mario.pixel_x) if ends_on_stall else None
        self.end_reason: EndReason | None = None

    @property
    def is_over(self) -> bool:
        return self.end_reason is not None

    def step(self, buttons: int) -> None:
        if self.is_over:
            raise RuntimeError("the attempt is over")
        self.ticks_elapsed += 1
        if self.mario.is_changing_power_state:
            self.mario.continue_power_state_change(ControllerState(buttons))
        else:
            self._play_one_tick(ControllerState(buttons))
        if self._stall_rule is not None:
            self._stall_rule.observe(self.mario.pixel_x)
        self.end_reason = self._reason_to_end()

    def result(self) -> AttemptResult:
        if not self.is_over:
            raise RuntimeError("the attempt is still running")
        return AttemptResult(
            end_reason=self.end_reason,
            furthest_x=self.furthest_x,
            ticks_elapsed=self.ticks_elapsed,
            final_score=self.scoreboard.score,
            coins_collected=self.scoreboard.coins,
            events=tuple(self.events),
        )

    def _play_one_tick(self, controller: ControllerState) -> None:
        pixel_x_before = self.mario.pixel_x
        self.mario.step(controller, self.tiles)
        if self.mario.head_hit_tile is not None:
            self._hit_block_from_below(*self.mario.head_hit_tile)
        self.scroll.follow(self.mario, self.mario.pixel_x - pixel_x_before)
        self.fireballs.step(self._playfield, self.enemies.active, self.ticks_elapsed)
        self.enemies.step(self._playfield)
        self.blocks.defeat_enemies_on_bumped_blocks(self.enemies.active, self.mario.x, self.ticks_elapsed)
        self._record_enemy_collisions(
            self._enemy_collision_check.step(self.ticks_elapsed, self.mario, self.enemies.active))
        self.items.step(self._playfield)
        self.blocks.knock_items_on_bumped_blocks(self.items.walking, self.mario.x)
        self._collect_touched_item()
        self.furthest_x = max(self.furthest_x, self.mario.pixel_x)
        self.blocks.step()
        self.level_timer.count_down()

    def _hit_block_from_below(self, column: int, row: int) -> None:
        head_hit = self.blocks.hit_from_below(column, row, self.ticks_elapsed, mario_is_big=self.mario.is_big)
        if head_hit is HeadHit.BUMPED_BLOCK:
            self.mario.bump_block()
        elif head_hit is HeadHit.BROKE_BRICK:
            self.mario.break_brick()

    def _record_enemy_collisions(self, outcome: EnemyCollisionOutcome) -> None:
        for points in outcome.points_per_stomp:
            self.events.append(GameEvent(self.ticks_elapsed, GameEventKind.DEFEATED_ENEMY, DefeatMethod.STOMP))
            if points is not None:
                self.scoreboard.score_points(points, self.ticks_elapsed)
        if outcome.mario_took_damage:
            self.events.append(GameEvent(self.ticks_elapsed, GameEventKind.TOOK_DAMAGE))
            self.fireballs.clear()
        self._died_to_enemy = outcome.mario_died

    def _collect_touched_item(self) -> None:
        """The item is an enemy object to the original, checked against Mario
        after the enemies and on the same ticks, and only while nothing has hurt
        him (PlayerEnemyCollision)."""
        if not is_enemy_check_tick(self.ticks_elapsed) or self._died_to_enemy or self.mario.is_changing_power_state:
            return
        item = self.items.take_touched(self.mario.hitbox())
        if item is not None:
            self._collect(item)

    def _collect(self, item: Item) -> None:
        """HandlePowerUpCollision: the 1-UP gives a life; a Super Mushroom or a fire
        flower scores and powers Mario up."""
        if item.kind is ItemKind.ONE_UP_MUSHROOM:
            self.scoreboard.collect_one_up(self.ticks_elapsed)
            return
        self.events.append(GameEvent(self.ticks_elapsed, item.collected_event_kind))
        self.scoreboard.score_points(ITEM_POINTS, self.ticks_elapsed)
        self.mario.power_up()

    def _reason_to_end(self) -> EndReason | None:
        if self._died_to_enemy:
            return EndReason.DIED_TO_ENEMY
        if self.mario.has_fallen_in_pit:
            return EndReason.FELL_IN_PIT
        if self.level_timer.has_run_out:
            return EndReason.TIMER_RAN_OUT
        if self._stall_rule is not None and self._stall_rule.has_stalled:
            return EndReason.STALLED
        return None
