"""One Attempt's score, coins and 1-UPs, as the original counts them.

Every change is also a game event: points as scored_points (the amount as its
detail), a coin as collected_coin followed by its 200 points (GiveOneCoin), a
1-UP as collected_one_up. Only play mode turns 1-UPs into lives (PlaySession).
"""

from mario.constants.scoring import COIN_POINTS
from mario.simulation.attempt_result import GameEvent, GameEventKind


class Scoreboard:
    def __init__(self, events: list[GameEvent]):
        self._events = events
        self.score = 0
        self.coins = 0
        self.one_ups = 0

    def collect_one_up(self, tick: int) -> None:
        self.one_ups += 1
        self._events.append(GameEvent(tick, GameEventKind.COLLECTED_ONE_UP))

    def score_points(self, points: int, tick: int) -> None:
        self.score += points
        self._events.append(GameEvent(tick, GameEventKind.SCORED_POINTS, points))

    def score_points_if_any(self, points: int | None, tick: int) -> None:
        """Points from a step of the score table; None, a step beyond it (a 1-UP in
        the original, not reproduced), scores nothing."""
        if points is not None:
            self.score_points(points, tick)

    def collect_coin(self, tick: int) -> None:
        self.coins += 1
        self._events.append(GameEvent(tick, GameEventKind.COLLECTED_COIN))
        self.score_points(COIN_POINTS, tick)
