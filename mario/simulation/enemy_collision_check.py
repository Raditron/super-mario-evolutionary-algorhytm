"""The Mario-vs-enemy check (the original's PlayerEnemyCollision), run every other tick.

Touching a still shell kicks it, from any side (HandlePECollisions). Touching any
other enemy while moving down at 1 px/f or more stomps it, and so does any touch
on a tick he has already stomped one. Any other touch hurts him
(ChkForPlayerInjury, ForceInjury): it kills small Mario and makes big Mario
small, after which he can't be hurt for a while. Once he is hurt, no further
enemy is checked that tick, since the original only checks while its player
control routine runs.

A touch counts once: an enemy that touched him at the last check and still does
is let be until a check finds them apart (Enemy_CollisionBits d0), so a shell he
has just kicked doesn't hurt him on its way out.

Where his feet are doesn't matter, as in the original (ChkForPlayerInjury): he
falls up to about 9 px between two checks, more than half a Goomba.
"""

from dataclasses import dataclass

from mario.constants.physics import ENEMY_CHECK_TICK_INTERVAL, STOMP_MIN_FALL_SPEED
from mario.simulation.enemy import Enemy
from mario.simulation.mario import Mario
from mario.simulation.stomp_chain import StompChain


def is_enemy_check_tick(tick: int) -> bool:
    """Whether Mario is checked against enemy objects (and so the item) on this
    tick: every other one (FrameCounter bit 0 clear)."""
    return tick % ENEMY_CHECK_TICK_INTERVAL == 0


@dataclass(frozen=True)
class EnemyCollisionOutcome:
    """What one tick's check found: the points each stomp and each shell kick
    scored, in order (None beyond the score table), and whether an enemy hurt big
    Mario or killed small Mario."""
    points_per_stomp: tuple[int | None, ...] = ()
    points_per_kick: tuple[int | None, ...] = ()
    mario_took_damage: bool = False
    mario_died: bool = False


class EnemyCollisionCheck:
    def __init__(self):
        self._stomp_chain = StompChain()
        self._enemies_touching_mario: set[Enemy] = set()

    def step(self, tick: int, mario: Mario, enemies: list[Enemy]) -> EnemyCollisionOutcome:
        """One tick, after Mario and the enemies have moved. A stomp squashes the
        enemy and bounces Mario at once."""
        if mario.is_on_ground:
            self._stomp_chain.land()
        if not is_enemy_check_tick(tick):
            return EnemyCollisionOutcome()
        return self._check(mario, enemies)

    def _check(self, mario: Mario, enemies: list[Enemy]) -> EnemyCollisionOutcome:
        self._stomp_chain.start_tick()
        points_per_stomp = []
        points_per_kick = []
        for enemy in enemies:
            if enemy.is_defeated or not self._is_new_touch(mario, enemy):
                continue
            if enemy.can_be_kicked:
                points_per_kick.append(self._kick(mario, enemy))
            elif mario.velocity_y >= STOMP_MIN_FALL_SPEED or self._stomp_chain.stomped_this_tick:
                points_per_stomp.append(self._stomp(mario, enemy))
            elif not mario.is_invulnerable:
                mario.get_hurt()
                return EnemyCollisionOutcome(tuple(points_per_stomp), tuple(points_per_kick),
                                             mario_took_damage=not mario.is_dead, mario_died=mario.is_dead)
        return EnemyCollisionOutcome(tuple(points_per_stomp), tuple(points_per_kick))

    def _is_new_touch(self, mario: Mario, enemy: Enemy) -> bool:
        """Whether they touch now but didn't at the last check."""
        if not enemy.hitbox().overlaps(mario.hitbox()):
            self._enemies_touching_mario.discard(enemy)
            return False
        if enemy in self._enemies_touching_mario:
            return False
        self._enemies_touching_mario.add(enemy)
        return True

    def _stomp(self, mario: Mario, enemy: Enemy) -> int | None:
        enemy.stomp()
        mario.bounce_off_enemy()
        return self._stomp_chain.stomp()

    def _kick(self, mario: Mario, shell: Enemy) -> int | None:
        points = self._stomp_chain.kick_points(shell.interval_ticks_left)
        shell.kick(mario.x)
        return points
