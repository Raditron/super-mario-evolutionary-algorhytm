"""Watch-live's picture (#29, spec section 8): the followed agent solid with his world,
the other living agents as translucent ghosts (outlines in the Debug view), and
the HUD's line `generation N · alive A / P · reached flag F`. Drawn through the
Viewer every mode shares."""

from dataclasses import replace

import pygame
import pytest

from mario.constants.view import GENERATION_LINE_TOP_LEFT, MARIO_COLOUR, SKY_COLOUR
from mario.level.static_level import StaticLevel
from mario.simulation.attempt import Attempt
from mario.snapshots.world_snapshot import AgentSnapshot, Area, GenerationProgress, MarioSnapshot, WorldSnapshot
from mario.view.hud import generation_line
from mario.view.viewer import Viewer
from tests.game.scripted_window import F1_PRESSED, NOTHING_PRESSED, ScriptedWindow

GHOST_BOX = (150, 100, 12, 14)                      # x, y, width, height in level pixels, in open sky
LINE_AREA = pygame.Rect(GENERATION_LINE_TOP_LEFT, (160, 10))
PROGRESS = GenerationProgress(generation=4, alive=37, population_size=50, reached_flag=2)


@pytest.fixture
def fonts():
    pygame.font.init()
    yield
    pygame.font.quit()


def sky_world() -> WorldSnapshot:
    """Open sky, no ground: Mario where an Attempt starts him."""
    return WorldSnapshot.of(Attempt(StaticLevel(["." * 20] * 15)))


def ghost(box: tuple[int, int, int, int] = GHOST_BOX) -> AgentSnapshot:
    return AgentSnapshot(1, MarioSnapshot(*box), True, Area.LEVEL, True, False)


def shown_frames(snapshot: WorldSnapshot, tmp_path, toggles_to_debug: bool = False) -> list[pygame.Surface]:
    """The snapshot drawn by the shared Viewer in the Sprite view (no sprites: hitbox colours), or the Debug view."""
    window = ScriptedWindow([F1_PRESSED if toggles_to_debug else NOTHING_PRESSED])
    viewer = Viewer.with_both_views(window, tmp_path)
    viewer.handle_events()
    viewer.show(snapshot)
    return window.frames_shown


def colour(frame: pygame.Surface, point: tuple[int, int]) -> tuple[int, int, int]:
    return tuple(frame.get_at(point))[:3]


def ghost_centre(snapshot: WorldSnapshot) -> tuple[int, int]:
    x, y, width, height = GHOST_BOX
    return x + width // 2 - snapshot.screen_left_x_pixels, y + height // 2


def test_the_sprite_view_draws_a_ghost_translucent_over_the_level(fonts, tmp_path):
    snapshot = replace(sky_world(), ghosts=(ghost(),))
    [frame] = shown_frames(snapshot, tmp_path)
    ghost_colour = colour(frame, ghost_centre(snapshot))
    assert ghost_colour not in (SKY_COLOUR, MARIO_COLOUR)
    # a blend of the two: each channel lies between the sky's and Mario's
    assert all(min(sky, mario) <= blended <= max(sky, mario)
               for sky, mario, blended in zip(SKY_COLOUR, MARIO_COLOUR, ghost_colour))


def test_the_debug_view_draws_a_ghost_as_its_hitboxs_outline(fonts, tmp_path):
    snapshot = replace(sky_world(), ghosts=(ghost(),))
    [frame] = shown_frames(snapshot, tmp_path, toggles_to_debug=True)
    x, y, _, _ = GHOST_BOX
    assert colour(frame, (x - snapshot.screen_left_x_pixels, y)) == MARIO_COLOUR
    assert colour(frame, ghost_centre(snapshot)) == SKY_COLOUR


@pytest.mark.parametrize("toggles_to_debug", [False, True], ids=["sprite-view", "debug-view"])
def test_the_followed_agent_is_drawn_solid_over_a_ghost_in_his_place(fonts, tmp_path, toggles_to_debug):
    world = sky_world()
    mario = world.mario
    snapshot = replace(world, ghosts=(ghost((mario.x_pixels, mario.y_pixels, mario.width_pixels,
                                             mario.height_pixels)),))
    [frame] = shown_frames(snapshot, tmp_path, toggles_to_debug)
    centre = (mario.x_pixels + mario.width_pixels // 2 - world.screen_left_x_pixels,
              mario.y_pixels + mario.height_pixels // 2)
    assert colour(frame, centre) == MARIO_COLOUR


def test_the_hud_shows_the_generations_line_only_while_a_generation_is_watched(fonts, tmp_path):
    world = sky_world()
    [unwatched] = shown_frames(world, tmp_path)
    [watched] = shown_frames(replace(world, generation_progress=PROGRESS), tmp_path)
    [later] = shown_frames(replace(world, generation_progress=replace(PROGRESS, alive=12)), tmp_path)
    line_of = lambda frame: pygame.image.tobytes(frame.subsurface(LINE_AREA), "RGB")
    assert all(colour(unwatched, point) == SKY_COLOUR
               for point in [(x, y) for x in range(LINE_AREA.left, LINE_AREA.right)
                             for y in range(LINE_AREA.top, LINE_AREA.bottom)])
    assert line_of(watched) != line_of(unwatched)
    assert line_of(later) != line_of(watched)


def test_the_generations_line_reads_as_the_spec_writes_it():
    assert generation_line(PROGRESS) == "generation 4 · alive 37 / 50 · reached flag 2"
