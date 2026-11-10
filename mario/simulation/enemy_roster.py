"""One Attempt's enemies: the active ones, and the spawner that adds the rest as the screen scrolls.

Active enemies move every tick. One is removed once it is well off the left of
the screen, has fallen below it, or is gone after being defeated. Newly
activated enemies start moving on the next tick.
"""

from mario.constants.level import ENEMY_REMOVAL_RANGE_PIXELS
from mario.level.static_level import EnemySpawn
from mario.simulation.playfield import Playfield
from mario.simulation.enemy import Enemy
from mario.simulation.enemy_spawner import EnemySpawner


class EnemyRoster:
    def __init__(self, spawns: tuple[EnemySpawn, ...]):
        self.active: list[Enemy] = []
        self._spawner = EnemySpawner(spawns)

    def step(self, playfield: Playfield, tick: int) -> None:
        for enemy in self.active:
            enemy.step(playfield.tiles, tick)
        screen_left_x_pixels = playfield.screen_left_x_pixels
        self.active = [enemy for enemy in self.active if not self._is_out_of_play(enemy, screen_left_x_pixels)]
        self.active += self._spawner.activate_due(screen_left_x_pixels)

    def remove_active(self) -> None:
        """A new area: the active enemies are gone; those still to come stay in the list."""
        self.active = []

    @staticmethod
    def _is_out_of_play(enemy: Enemy, screen_left_x_pixels: int) -> bool:
        return (enemy.hitbox().x_pixels < screen_left_x_pixels - ENEMY_REMOVAL_RANGE_PIXELS
                or enemy.has_fallen_out or enemy.is_gone)
