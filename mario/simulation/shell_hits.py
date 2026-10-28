"""A moving shell against the other enemies (the original's EnemiesCollision,
ProcEnemyCollisions and ShellCollisions).

Every other tick, on the ticks Mario isn't checked against enemies (FrameCounter
bit 0 set), a moving shell defeats each enemy it touches. Both must be on the
screen. Each defeat climbs the shell's own chain of the score table, which is
never reset while it is a shell, and the enemy it defeats jumps away from Mario
and falls out of the level, as a fireball's does.
"""

from mario.constants.scoring import SHELL_DEFEAT_STEPS_PAST_SHELL_CHAIN
from mario.simulation.attempt_result import DefeatMethod, GameEvent, GameEventKind
from mario.simulation.enemy import Enemy
from mario.simulation.enemy_collision_check import is_enemy_check_tick
from mario.simulation.koopa import Koopa
from mario.simulation.scoreboard import Scoreboard
from mario.simulation.stomp_chain import score_table_points


class ShellHits:
    def __init__(self, scoreboard: Scoreboard, events: list[GameEvent]):
        self._scoreboard = scoreboard
        self._events = events

    def step(self, enemies: list[Enemy], screen_left_x_pixels: int, mario_x: int, tick: int) -> None:
        """One tick, after the enemies have moved."""
        if is_enemy_check_tick(tick):
            return
        for shell in enemies:
            if not (isinstance(shell, Koopa) and shell.is_moving_shell and shell.can_be_hit(screen_left_x_pixels)):
                continue
            for enemy in enemies:
                if (enemy is not shell and enemy.can_be_hit(screen_left_x_pixels)
                        and enemy.hitbox().overlaps(shell.hitbox())):
                    self._defeat(enemy, shell, mario_x, tick)

    def _defeat(self, enemy: Enemy, shell: Koopa, mario_x: int, tick: int) -> None:
        enemy.defeat_by_shell(mario_x)
        self._events.append(GameEvent(tick, GameEventKind.DEFEATED_ENEMY, DefeatMethod.KICKED_SHELL))
        points = score_table_points(shell.shell_defeats + SHELL_DEFEAT_STEPS_PAST_SHELL_CHAIN)
        shell.shell_defeats += 1
        if points is not None:
            self._scoreboard.score_points(points, tick)
