"""The Debug view's list of recent game events, with the points scored, newest last."""

import pygame

from mario.constants.view import DEBUG_GAME_EVENT_LINES, DEBUG_GAME_EVENTS_TOP_LEFT
from mario.simulation.attempt_result import GameEvent
from mario.view.debug_text import DebugText


class GameEventFeed:
    def __init__(self, text: DebugText):
        self._text = text

    def draw(self, recent_events: tuple[GameEvent, ...], screen: pygame.Surface) -> None:
        lines = [_describe(event) for event in recent_events[-DEBUG_GAME_EVENT_LINES:]]
        self._text.draw_lines(lines, DEBUG_GAME_EVENTS_TOP_LEFT, screen)


def _describe(event: GameEvent) -> str:
    """Its tick, kind and detail: a scored_points event's detail is the points scored."""
    return " ".join(str(part) for part in (event.tick, event.kind, event.detail) if part is not None)
