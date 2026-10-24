"""The Debug view draws Goombas as coloured hitboxes, a squashed one flattened (#17)."""

import pygame

from mario.constants.level import SCREEN_HEIGHT_PIXELS, SCREEN_WIDTH_PIXELS
from mario.constants.view import GOOMBA_COLOUR, SKY_COLOUR
from mario.level.static_level import EnemyKind
from mario.snapshots.world_snapshot import EnemySnapshot, HudSnapshot, MarioSnapshot, VisibleTiles, WorldSnapshot
from mario.view.debug_renderer import DebugRenderer

SCREEN_LEFT_X = 100
GOOMBA_X, GOOMBA_Y = 300, 120                 # in level pixels, clear of the ground and Mario


def drawn_with(goomba: EnemySnapshot) -> pygame.Surface:
    """A screen with no tiles, Mario at its left and the Goomba."""
    snapshot = WorldSnapshot(tick=0, screen_left_x_pixels=SCREEN_LEFT_X, tiles=VisibleTiles(0, ()),
                             mario=MarioSnapshot(SCREEN_LEFT_X, 194, 12, 14), enemies=(goomba,),
                             hud=HudSnapshot(0, 0, 400))
    screen = pygame.Surface((SCREEN_WIDTH_PIXELS, SCREEN_HEIGHT_PIXELS))
    DebugRenderer().draw(snapshot, screen)
    return screen


def colour_at(screen: pygame.Surface, level_x: int, y: int) -> tuple[int, int, int]:
    return tuple(screen.get_at((level_x - SCREEN_LEFT_X, y)))[:3]


def test_a_goomba_is_drawn_as_its_hitbox_in_the_goomba_colour():
    screen = drawn_with(EnemySnapshot(EnemyKind.GOOMBA, GOOMBA_X, GOOMBA_Y, 16, 16, is_defeated=False))
    assert colour_at(screen, GOOMBA_X, GOOMBA_Y) == GOOMBA_COLOUR
    assert colour_at(screen, GOOMBA_X + 15, GOOMBA_Y + 15) == GOOMBA_COLOUR
    assert colour_at(screen, GOOMBA_X + 16, GOOMBA_Y) == SKY_COLOUR
    assert colour_at(screen, GOOMBA_X, GOOMBA_Y - 1) == SKY_COLOUR


def test_a_squashed_goomba_is_drawn_flattened_onto_its_feet():
    screen = drawn_with(EnemySnapshot(EnemyKind.GOOMBA, GOOMBA_X, GOOMBA_Y, 16, 16, is_defeated=True))
    assert colour_at(screen, GOOMBA_X, GOOMBA_Y) == SKY_COLOUR
    assert colour_at(screen, GOOMBA_X, GOOMBA_Y + 15) == GOOMBA_COLOUR
