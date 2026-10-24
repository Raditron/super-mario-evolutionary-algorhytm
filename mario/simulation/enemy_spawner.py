"""Enemy activation (the original's ProcessEnemyData), without its 5-slot limit.

Enemies are read from the level's spawn table strictly in order. The next one
activates once its activation x is at most 48 px past the screen's right edge;
one already left of that edge when its turn comes is skipped for good.
"""

from mario.constants.level import ENEMY_ACTIVATION_RANGE_PIXELS, SCREEN_WIDTH_PIXELS
from mario.level.static_level import EnemyKind, EnemySpawn
from mario.simulation.enemy import Enemy
from mario.simulation.goomba import Goomba

# The Koopa joins with its own slice (#22); until then its turn in the list passes without one.
ENEMY_CLASS_BY_KIND = {EnemyKind.GOOMBA: Goomba}


class EnemySpawner:
    def __init__(self, spawns: tuple[EnemySpawn, ...]):
        self._spawns = spawns
        self._next_spawn_index = 0

    def activate_due(self, screen_left_x_pixels: int) -> list[Enemy]:
        """The enemies whose turn has come with the screen's left edge here."""
        screen_right_x_pixels = screen_left_x_pixels + SCREEN_WIDTH_PIXELS - 1
        activated = []
        while self._next_spawn_index < len(self._spawns):
            spawn = self._spawns[self._next_spawn_index]
            if spawn.activation_x_pixels > screen_right_x_pixels + ENEMY_ACTIVATION_RANGE_PIXELS:
                break
            self._next_spawn_index += 1
            enemy_class = ENEMY_CLASS_BY_KIND.get(spawn.kind)
            if spawn.activation_x_pixels >= screen_right_x_pixels and enemy_class is not None:
                activated.append(enemy_class(spawn))
        return activated
