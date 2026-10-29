"""One Attempt: one life of one Mario in a freshly loaded level.

Its one way in is step(buttons), one tick given that tick's Controller bitmask.
Once it has ended with reached_flag, and in play or replay only, a second one
opens: step_end_of_level(), one input-free tick of its EndOfLevelSequence. It
uses no randomness, no floats and no wall clock, so the same Controller log
always gives the same Attempt.

It ends when Mario dies, touches the flagpole or the level timer runs out, and,
if the mode turns the stall rule on (training does, play doesn't), when he
stalls. Down on the warp pipe takes him into the bonus room, and its exit pipe
back to the level (PipeTransition): meanwhile he can't be controlled, the level
timer and the stall count stand still, and everything else moves on without
touching him. Each change of area starts the area afresh: only his power state
goes with him. The touch scores the flag-height and remaining-time points at once, and
ends the tick there: the level timer stops, and nothing else moves (the slide and
castle walk after it are step_end_of_level's). While Mario
grows, shrinks or catches fire, everything else stands still, the level timer
too, but for his fireballs, which the original runs every frame; the ticks
still count, and so does the stall rule. Once everything has moved, Mario picks
the animation frame he shows (Mario.animate), on the flagpole and on his castle
walk too.
"""

from mario.constants.level import CHECKPOINT_LEFT_X_PIXELS, SCROLL_STOP_LEFT_X_PIXELS
from mario.constants.scoring import ITEM_POINTS
from mario.constants.warp_pipe import (
    BONUS_ROOM_START_SPRITE_X_PIXELS,
    BONUS_ROOM_START_SPRITE_Y_PIXELS,
    PAGE_WIDTH_PIXELS,
    RETURN_SPRITE_X_IN_PAGE_PIXELS,
    RETURN_START_SPRITE_Y_PIXELS,
)
from mario.controller.controller_state import ControllerState
from mario.level.static_level import StaticLevel
from mario.simulation.area import Area
from mario.simulation.attempt_result import AttemptResult, DefeatMethod, EndReason, GameEvent, GameEventKind
from mario.simulation.attempt_tiles import AttemptTiles
from mario.simulation.blocks import Blocks, HeadHit
from mario.simulation.enemy_collision_check import EnemyCollisionCheck, EnemyCollisionOutcome, is_enemy_check_tick
from mario.simulation.end_of_level_sequence import WALK_RIGHT, EndOfLevelSequence
from mario.simulation.enemy_roster import EnemyRoster
from mario.simulation.fireballs import Fireballs
from mario.simulation.flagpole import Flag, FlagpoleTouch, touches_flagpole
from mario.simulation.items import Items
from mario.simulation.level_timer import LevelTimer
from mario.simulation.mario import Mario
from mario.simulation.pipe_transition import (
    DroppingIntoBonusRoom,
    PipeTransition,
    RisingOutOfPipe,
    SinkingIntoWarpPipe,
    WalkingIntoExitPipe,
    steps_into_warp_pipe,
    walks_into_exit_pipe,
)
from mario.simulation.playfield import Playfield
from mario.simulation.item_kind import ItemKind
from mario.simulation.item import Item
from mario.simulation.scoreboard import Scoreboard
from mario.simulation.scroll import Scroll
from mario.simulation.shell_hits import ShellHits
from mario.simulation.stall_rule import StallRule


class Attempt:
    def __init__(self, level: StaticLevel, *, ends_on_stall: bool = False, from_checkpoint: bool = False):
        """ends_on_stall turns the stall rule on. from_checkpoint starts Mario
        with the screen's left edge at the checkpoint (play mode only)."""
        screen_left_x_pixels = CHECKPOINT_LEFT_X_PIXELS if from_checkpoint else 0
        self.level = level
        self.area = Area.LEVEL
        # The area Mario is in: its tiles, the blocks in them, and its screen.
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
        self._shell_hits = ShellHits(self.scoreboard, self.events)
        self._stall_rule = StallRule(self.mario.pixel_x) if ends_on_stall else None
        self.flagpole_touch: FlagpoleTouch | None = None
        self.end_of_level: EndOfLevelSequence | None = None
        self.flag = Flag(level.flagpole_column) if level.flagpole_column is not None else None
        self.end_reason: EndReason | None = None
        self._pipe_transition: PipeTransition | None = None
        # The level's tiles and blocks, kept while Mario is in the bonus room.
        self._level_tiles = self.tiles
        self._level_blocks = self.blocks

    @property
    def is_over(self) -> bool:
        return self.end_reason is not None

    @property
    def is_mario_controlled(self) -> bool:
        """False while a pipe transition moves him."""
        return self._pipe_transition is None

    def step(self, buttons: int) -> None:
        if self.is_over:
            raise RuntimeError("the attempt is over")
        self.ticks_elapsed += 1
        is_controlled = self._pipe_transition is None
        if self.mario.is_changing_power_state:
            self.mario.continue_power_state_change(ControllerState(buttons))
            self.fireballs.step(self._playfield, self.enemies.active, self.ticks_elapsed)
        elif is_controlled:
            self._play_one_tick(ControllerState(buttons))
        else:
            self._continue_pipe_transition()
        if self._stall_rule is not None and is_controlled:
            self._stall_rule.observe(self.mario.pixel_x)
        self.end_reason = self._reason_to_end()

    def step_end_of_level(self) -> None:
        """After reached_flag, in play and replay only: one input-free tick of the
        end of the level, starting on the touch's own tick. Walking to the castle,
        Mario moves as step moves him, pressing right, and the screen follows."""
        if self.end_of_level is None:
            raise RuntimeError("the attempt did not reach the flag")
        if self.end_of_level.is_walking_to_the_castle:
            self._move_mario(WALK_RIGHT)
        if self.end_of_level.mario_still_moves:
            self.mario.animate(self.ticks_elapsed)
        self.end_of_level.step()

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
        self._move_mario(controller)
        if self.area is Area.LEVEL:
            self.furthest_x = max(self.furthest_x, self.mario.pixel_x)
        for _ in range(self.tiles.take_coins_touched_by(self.mario.hitbox())):
            self.scoreboard.collect_coin(self.ticks_elapsed)
        if touches_flagpole(self.mario, self.tiles):
            self._touch_flagpole()
            return
        self._start_pipe_transition_if_due(controller)
        # A transition starting now already keeps him out of play (the original's
        # game routine is no longer 8), and stops the level timer.
        mario_is_in_play = self._pipe_transition is None
        self._step_everything_but_mario(mario_is_in_play)
        if mario_is_in_play:
            self.level_timer.count_down()
        self.mario.animate(self.ticks_elapsed)

    def _step_everything_but_mario(self, mario_is_in_play: bool) -> None:
        """Fireballs, enemies, items and blocks; only while Mario is in play do the
        enemies and the item touch him."""
        self.fireballs.step(self._playfield, self.enemies.active, self.ticks_elapsed)
        self.enemies.step(self._playfield, self.ticks_elapsed)
        self._shell_hits.step(self.enemies.active, self.scroll.left_x_pixels, self.mario.x, self.ticks_elapsed)
        self.blocks.defeat_enemies_on_bumped_blocks(self.enemies.active, self.mario.x, self.ticks_elapsed)
        if mario_is_in_play:
            self._record_enemy_collisions(
                self._enemy_collision_check.step(self.ticks_elapsed, self.mario, self.enemies.active))
        self.items.step(self._playfield)
        self.blocks.knock_items_on_bumped_blocks(self.items.walking, self.mario.x)
        if mario_is_in_play:
            self._collect_touched_item()
        self.blocks.step()

    def _start_pipe_transition_if_due(self, controller: ControllerState) -> None:
        if self.area is Area.LEVEL and steps_into_warp_pipe(self.mario, controller, self.level.warp_pipe):
            self.events.append(GameEvent(self.ticks_elapsed, GameEventKind.ENTERED_PIPE))
            self._pipe_transition = SinkingIntoWarpPipe(self.mario)
        elif self.area is Area.BONUS_ROOM and walks_into_exit_pipe(self.mario, self.level.bonus_room):
            self._pipe_transition = WalkingIntoExitPipe(self.mario)

    def _continue_pipe_transition(self) -> None:
        """One tick of it; on the tick it moves Mario to another area, nothing else
        moves (the original's game engine doesn't run as the area changes)."""
        transition = self._pipe_transition
        transition.step()
        if transition.is_over:
            self._pipe_transition = None
            if transition.area_after is Area.BONUS_ROOM:
                self._enter_bonus_room()
                return
            if transition.area_after is Area.LEVEL:
                self._come_back_to_level()
                return
        self._step_everything_but_mario(mario_is_in_play=False)

    def _enter_bonus_room(self) -> None:
        """He arrives at the top of the room, to drop in."""
        self._level_tiles, self._level_blocks = self.tiles, self.blocks
        room_tiles = AttemptTiles(self.level.bonus_room.tiles)
        self._start_area(Area.BONUS_ROOM, room_tiles, Blocks(room_tiles, self.scoreboard, self.items, self.events),
                         BONUS_ROOM_START_SPRITE_X_PIXELS, BONUS_ROOM_START_SPRITE_Y_PIXELS,
                         screen_left_x_pixels=0, screen_stop_left_x_pixels=0)
        self._pipe_transition = DroppingIntoBonusRoom(self.mario, self.tiles)

    def _come_back_to_level(self) -> None:
        """He arrives below the screen at the return page, under the level's pipe,
        to rise out of it; the furthest x he has reached jumps there."""
        screen_left_x_pixels = self.level.bonus_room.return_page * PAGE_WIDTH_PIXELS
        self._start_area(Area.LEVEL, self._level_tiles, self._level_blocks,
                         screen_left_x_pixels + RETURN_SPRITE_X_IN_PAGE_PIXELS, RETURN_START_SPRITE_Y_PIXELS,
                         screen_left_x_pixels, SCROLL_STOP_LEFT_X_PIXELS)
        self.furthest_x = max(self.furthest_x, self.mario.pixel_x)
        self.events.append(GameEvent(self.ticks_elapsed, GameEventKind.EXITED_PIPE))
        self._pipe_transition = RisingOutOfPipe(self.mario)

    def _start_area(self, area: Area, tiles: AttemptTiles, blocks: Blocks, mario_sprite_x_pixels: int,
                    mario_sprite_y_pixels: int, screen_left_x_pixels: int, screen_stop_left_x_pixels: int) -> None:
        """An area starts afresh (InitializeArea): Mario with only his power state
        kept, no enemy, item or fireball, the level timer's unit begun again, and a
        new stall record."""
        self.area = area
        self.tiles = tiles
        self.blocks = blocks
        self.mario.start_in_area(mario_sprite_x_pixels, mario_sprite_y_pixels)
        self.scroll = Scroll(self.mario.pixel_x, screen_left_x_pixels, screen_stop_left_x_pixels)
        self._playfield = Playfield(tiles, self.scroll)
        self.enemies.remove_active()
        self.items.remove_all()
        self.fireballs.remove_all()
        self.level_timer.restart_unit()
        if self._stall_rule is not None:
            self._stall_rule.start_again(self.mario.pixel_x)

    def _touch_flagpole(self) -> None:
        self.flagpole_touch = FlagpoleTouch.of(self.mario, self.level_timer.time_left)
        self.scoreboard.score_points(self.flagpole_touch.flag_points, self.ticks_elapsed)
        self.scoreboard.score_points(self.flagpole_touch.time_points, self.ticks_elapsed)
        self.end_of_level = EndOfLevelSequence(self.mario, self.tiles, self.flag, self.flagpole_touch,
                                               self.level.flagpole_column)

    def _move_mario(self, controller: ControllerState) -> None:
        """Mario moves, any block his head hit is hit, and the screen follows him."""
        pixel_x_before = self.mario.pixel_x
        self.mario.step(controller, self.tiles)
        if self.mario.head_hit_tile is not None:
            self._hit_block_from_below(*self.mario.head_hit_tile)
        self.scroll.follow(self.mario, self.mario.pixel_x - pixel_x_before)

    def _hit_block_from_below(self, column: int, row: int) -> None:
        head_hit = self.blocks.hit_from_below(column, row, self.ticks_elapsed, mario_is_big=self.mario.is_big)
        if head_hit is HeadHit.BUMPED_BLOCK:
            self.mario.bump_block()
        elif head_hit is HeadHit.BROKE_BRICK:
            self.mario.break_brick()

    def _record_enemy_collisions(self, outcome: EnemyCollisionOutcome) -> None:
        for points in outcome.points_per_stomp:
            self.events.append(GameEvent(self.ticks_elapsed, GameEventKind.DEFEATED_ENEMY, DefeatMethod.STOMP))
            self.scoreboard.score_points_if_any(points, self.ticks_elapsed)
        for points in outcome.points_per_kick:
            self.events.append(GameEvent(self.ticks_elapsed, GameEventKind.KICKED_SHELL))
            self.scoreboard.score_points_if_any(points, self.ticks_elapsed)
        for points in outcome.points_per_starman_defeat:
            self.events.append(GameEvent(self.ticks_elapsed, GameEventKind.DEFEATED_ENEMY, DefeatMethod.STARMAN))
            self.scoreboard.score_points(points, self.ticks_elapsed)
        if outcome.mario_took_damage:
            self.events.append(GameEvent(self.ticks_elapsed, GameEventKind.TOOK_DAMAGE))
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
        flower scores and powers Mario up; a Starman scores and makes him invincible."""
        if item.kind is ItemKind.ONE_UP_MUSHROOM:
            self.scoreboard.collect_one_up(self.ticks_elapsed)
            return
        self.events.append(GameEvent(self.ticks_elapsed, item.collected_event_kind))
        self.scoreboard.score_points(ITEM_POINTS, self.ticks_elapsed)
        if item.kind is ItemKind.STARMAN:
            self.mario.become_invincible()
        else:
            self.mario.power_up()

    def _reason_to_end(self) -> EndReason | None:
        if self.flagpole_touch is not None:
            return EndReason.REACHED_FLAG
        if self._died_to_enemy:
            return EndReason.DIED_TO_ENEMY
        if self.mario.has_fallen_in_pit:
            return EndReason.FELL_IN_PIT
        if self.level_timer.has_run_out:
            return EndReason.TIMER_RAN_OUT
        if self._stall_rule is not None and self._stall_rule.has_stalled:
            return EndReason.STALLED
        return None
