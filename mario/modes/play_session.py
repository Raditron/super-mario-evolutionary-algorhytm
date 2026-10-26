"""A human's game of World 1-1, life after life (play mode only; training never sees it).

Each life is its own Attempt in a freshly loaded level, with no stall rule.
The game starts with 3 lives and gains one for every 100 coins. Score and coins
carry across lives. A life lost once the screen's left edge has reached the
checkpoint restarts there (PlayerLoseLife); losing the last life starts a new game.
"""

from mario.constants.level import CHECKPOINT_LEFT_X_PIXELS
from mario.constants.scoring import COINS_PER_EXTRA_LIFE, STARTING_LIVES
from mario.level.static_level import StaticLevel
from mario.simulation.attempt import Attempt
from mario.simulation.observation_builder import ObservationBuilder
from mario.snapshots.world_snapshot import HudSnapshot, WorldSnapshot


class PlaySession:
    def __init__(self, level: StaticLevel):
        self._level = level
        self._observation_builder = ObservationBuilder(level)
        self._start_new_game()

    @property
    def lives(self) -> int:
        return STARTING_LIVES + self._total_coins() // COINS_PER_EXTRA_LIFE - self._lives_lost

    @property
    def score(self) -> int:
        return self._score_before_this_life + self.attempt.scoreboard.score

    @property
    def coins(self) -> int:
        """The coin count the HUD shows, which restarts at 0 every 100 coins."""
        return self._total_coins() % COINS_PER_EXTRA_LIFE

    def step(self, buttons: int) -> None:
        """One tick of the current life; when it ends, the next one starts."""
        self.attempt.step(buttons)
        if self.attempt.is_over:
            self._lose_life()

    def snapshot(self) -> WorldSnapshot:
        hud = HudSnapshot(self.score, self.coins, self.attempt.level_timer.time_left)
        return WorldSnapshot.of(self.attempt, hud, self._observation_builder)

    def _start_new_game(self) -> None:
        self._lives_lost = 0
        self._score_before_this_life = 0
        self._coins_before_this_life = 0
        self.attempt = Attempt(self._level)

    def _lose_life(self) -> None:
        self._lives_lost += 1
        if self.lives == 0:
            self._start_new_game()
            return
        reached_checkpoint = self.attempt.scroll.left_x_pixels >= CHECKPOINT_LEFT_X_PIXELS
        self._score_before_this_life = self.score
        self._coins_before_this_life = self._total_coins()
        self.attempt = Attempt(self._level, from_checkpoint=reached_checkpoint)

    def _total_coins(self) -> int:
        return self._coins_before_this_life + self.attempt.scoreboard.coins
