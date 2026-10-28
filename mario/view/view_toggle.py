"""The two views of the level, one shown at a time; F1 switches between them (spec section 8)."""

from typing import Protocol

import pygame

from mario.snapshots.world_snapshot import WorldSnapshot


class View(Protocol):
    """A renderer: the Sprite view or the Debug view."""
    def draw(self, snapshot: WorldSnapshot, screen: pygame.Surface) -> None: ...


class ViewToggle:
    def __init__(self, first_view: View, second_view: View):
        """The first view is shown until the first toggle."""
        self._shown_view, self._hidden_view = first_view, second_view

    def toggle(self) -> None:
        self._shown_view, self._hidden_view = self._hidden_view, self._shown_view

    def draw(self, snapshot: WorldSnapshot, screen: pygame.Surface) -> None:
        self._shown_view.draw(snapshot, screen)
