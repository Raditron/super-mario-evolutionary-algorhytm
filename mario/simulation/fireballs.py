"""One Attempt's fireballs: the ones fire Mario has shot (ProcFireball_Bubble,
FireballObjCore).

He has two fireball slots. A shot takes the slot a shot counter points at
(FireballCounter's lowest bit), and only if that slot is free; so at most two
fly (or explode) at once. A fireball moves on the tick it is shot, before the
enemies move, as in the original's GameEngine. One that is gone (off the
screen, or done exploding) frees its slot.

Every other tick, as Mario is checked against enemies, a flying fireball that
touches enemies defeats each of them (FireballEnemyCollision, which goes on
checking the rest after a hit) and explodes. It skips those off the screen.
What a hit does to an enemy, and what it scores, is the enemy's to say.

The original runs and draws them only while Mario is fiery. Once fire Mario is
hurt, they stand still, unseen, in their slots (which stay taken), and fly on
from there if he becomes fiery again.
"""

from mario.constants.physics import FIREBALL_SLOTS
from mario.simulation.attempt_result import DefeatMethod, GameEvent, GameEventKind
from mario.simulation.enemy import Enemy
from mario.simulation.enemy_collision_check import is_enemy_check_tick
from mario.simulation.fireball import Fireball
from mario.simulation.mario import Mario
from mario.simulation.playfield import Playfield
from mario.simulation.scoreboard import Scoreboard


class Fireballs:
    def __init__(self, mario: Mario, scoreboard: Scoreboard, events: list[GameEvent]):
        self._mario = mario
        self._scoreboard = scoreboard
        self._events = events
        self._slots: list[Fireball | None] = [None] * FIREBALL_SLOTS
        self._shot_count = 0

    @property
    def active(self) -> list[Fireball]:
        """The fireballs in play: none unless Mario is fiery."""
        if not self._mario.is_fiery:
            return []
        return [fireball for fireball in self._slots if fireball is not None]

    def step(self, playfield: Playfield, enemies: list[Enemy], tick: int) -> None:
        """One tick, after Mario has moved: his shot, then every fireball."""
        if not self._mario.is_fiery:
            return
        if self._mario.wants_to_shoot_fireball:
            self._shoot(tick)
        for slot, fireball in enumerate(self._slots):
            if fireball is None:
                continue
            fireball.step(playfield)
            if fireball.is_gone:
                self._slots[slot] = None
            elif not fireball.is_exploding and is_enemy_check_tick(tick):
                self._hit_enemies(fireball, enemies, playfield.screen_left_x_pixels, tick)

    def _hit_enemies(self, fireball: Fireball, enemies: list[Enemy], screen_left_x_pixels: int, tick: int) -> None:
        """The original checks its enemy slots from the last down; the newest enemy
        is the nearest the replica has to the last slot."""
        for enemy in reversed(enemies):
            if enemy.can_be_hit(screen_left_x_pixels) and enemy.hitbox().overlaps(fireball.hitbox()):
                fireball.explode()
                enemy.defeat_by_fireball(self._mario.x)
                self._events.append(GameEvent(tick, GameEventKind.DEFEATED_ENEMY, DefeatMethod.FIREBALL))
                self._scoreboard.score_points(enemy.fireball_defeat_points, tick)

    def _shoot(self, tick: int) -> None:
        slot = self._shot_count % FIREBALL_SLOTS
        if self._slots[slot] is not None:
            return
        mario = self._mario
        self._slots[slot] = Fireball(mario.sprite_x_pixels, mario.sprite_y_pixels, mario.facing_direction)
        self._shot_count += 1
        self._events.append(GameEvent(tick, GameEventKind.SHOT_FIREBALL))
