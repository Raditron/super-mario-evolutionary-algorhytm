"""One Attempt's score and coins, as the original counts them.

Every change is also a game event: points as scored_points (the amount as its
detail), a coin as collected_coin followed by its 200 points (GiveOneCoin).
"""

from mario.constants.scoring import COIN_POINTS
from mario.simulation.attempt_result import GameEvent, GameEventKind


class Scoreboard:
    def __init__(self, events: list[GameEvent]):
        self._events = events
        self.score = 0
        self.coins = 0

    def score_points(self, points: int, tick: int) -> None:
        self.score += points
        self._events.append(GameEvent(tick, GameEventKind.SCORED_POINTS, points))

    def collect_coin(self, tick: int) -> None:
        self.coins += 1
        self._events.append(GameEvent(tick, GameEventKind.COLLECTED_COIN))
        self.score_points(COIN_POINTS, tick)
