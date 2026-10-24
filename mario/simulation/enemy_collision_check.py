"""The Mario-vs-enemy check (the original's PlayerEnemyCollision), run every other tick.

Touching an enemy while moving down at 1 px/f or more stomps it, and so does any
touch on a tick he has already stomped one; any other touch kills small Mario.

Where his feet are doesn't matter, as in the original (ChkForPlayerInjury): he
falls up to about 9 px between two checks, more than half a Goomba.
"""

from dataclasses import dataclass

from mario.constants.physics import ENEMY_CHECK_TICK_INTERVAL, STOMP_MIN_FALL_SPEED
from mario.simulation.enemy import Enemy
from mario.simulation.mario import Mario
from mario.simulation.stomp_chain import StompChain


@dataclass(frozen=True)
class EnemyCollisionOutcome:
    """What one tick's check found: the points each stomp scored, in order (None
    beyond the stomp chain's table), and whether an enemy killed Mario."""
    points_per_stomp: tuple[int | None, ...] = ()
    mario_died: bool = False


class EnemyCollisionCheck:
    def __init__(self):
        self._stomp_chain = StompChain()

    def step(self, tick: int, mario: Mario, enemies: list[Enemy]) -> EnemyCollisionOutcome:
        """One tick, after Mario and the enemies have moved. A stomp squashes the
        enemy and bounces Mario at once."""
        if mario.is_on_ground:
            self._stomp_chain.land()
        if tick % ENEMY_CHECK_TICK_INTERVAL != 0:
            return EnemyCollisionOutcome()
        return self._check(mario, enemies)

    def _check(self, mario: Mario, enemies: list[Enemy]) -> EnemyCollisionOutcome:
        self._stomp_chain.start_tick()
        points_per_stomp = []
        for enemy in enemies:
            if not enemy.is_harmful or not enemy.hitbox().overlaps(mario.hitbox()):
                continue
            if mario.velocity_y >= STOMP_MIN_FALL_SPEED or self._stomp_chain.stomped_this_tick:
                points_per_stomp.append(self._stomp(mario, enemy))
            else:
                return EnemyCollisionOutcome(tuple(points_per_stomp), mario_died=True)
        return EnemyCollisionOutcome(tuple(points_per_stomp))

    def _stomp(self, mario: Mario, enemy: Enemy) -> int | None:
        enemy.stomp()
        mario.bounce_off_enemy()
        return self._stomp_chain.stomp()
