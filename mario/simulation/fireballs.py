"""One Attempt's fireballs: the ones fire Mario has thrown (ProcFireball_Bubble,
FireballObjCore).

He has two fireball slots. A throw takes the slot a throw counter points at
(FireballCounter's lowest bit), and only if that slot is free; so at most two
fly (or explode) at once. A thrown fireball moves on the tick it is thrown,
before the enemies move, as in the original's GameEngine. One that is gone
(off the screen, or done exploding) frees its slot.

Every other tick, as Mario is checked against enemies, a flying fireball that
touches enemies defeats each of them (FireballEnemyCollision, which goes on
checking the rest after a hit) and explodes. What a hit does to an enemy, and
what it scores, is the enemy's to say.

Once fire Mario is hurt, his fireballs are gone: the original stops running and
drawing them as soon as he isn't fiery.
"""

from mario.constants.physics import FIREBALL_SLOTS
from mario.simulation.attempt_result import DefeatMethod, GameEvent, GameEventKind
from mario.simulation.attempt_tiles import AttemptTiles
from mario.simulation.enemy import Enemy
from mario.simulation.enemy_collision_check import is_enemy_check_tick
from mario.simulation.fireball import Fireball
from mario.simulation.mario import Mario
from mario.simulation.scoreboard import Scoreboard


class Fireballs:
    def __init__(self, scoreboard: Scoreboard, events: list[GameEvent]):
        self._scoreboard = scoreboard
        self._events = events
        self._slots: list[Fireball | None] = [None] * FIREBALL_SLOTS
        self._throw_count = 0

    @property
    def active(self) -> list[Fireball]:
        return [fireball for fireball in self._slots if fireball is not None]

    def step(self, mario: Mario, tiles: AttemptTiles, screen_left_x_pixels: int, enemies: list[Enemy],
             tick: int) -> None:
        """One tick, after Mario has moved: his throw, then every fireball."""
        if mario.wants_to_throw_fireball:
            self._throw(mario, tick)
        for slot, fireball in enumerate(self._slots):
            if fireball is None:
                continue
            fireball.step(tiles, screen_left_x_pixels)
            if fireball.is_gone:
                self._slots[slot] = None
            elif not fireball.is_exploding and is_enemy_check_tick(tick):
                self._hit_enemies(fireball, enemies, mario.x, tick)

    def clear(self) -> None:
        self._slots = [None] * FIREBALL_SLOTS

    def _hit_enemies(self, fireball: Fireball, enemies: list[Enemy], mario_x: int, tick: int) -> None:
        for enemy in enemies:
            if enemy.can_be_hit_by_fireball and enemy.hitbox().overlaps(fireball.hitbox()):
                fireball.explode()
                enemy.defeat_by_fireball(mario_x)
                self._events.append(GameEvent(tick, GameEventKind.DEFEATED_ENEMY, DefeatMethod.FIREBALL))
                self._scoreboard.score_points(enemy.fireball_defeat_points, tick)

    def _throw(self, mario: Mario, tick: int) -> None:
        slot = self._throw_count % FIREBALL_SLOTS
        if self._slots[slot] is not None:
            return
        self._slots[slot] = Fireball(mario.sprite_x_pixels, mario.sprite_y_pixels, mario.facing_direction)
        self._throw_count += 1
        self._events.append(GameEvent(tick, GameEventKind.SHOT_FIREBALL))
