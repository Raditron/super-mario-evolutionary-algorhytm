"""The knight's walk, captured to watch (#61): small and big Mario stand, walk,
let go, run and turn round on a flat level, each tick drawn by the real Sprite
view from assets/sprites/, and written out as an animated GIF per size and a
strip of frames, to the git-ignored test_output/ folder."""

from dataclasses import dataclass
from pathlib import Path

import pygame
import pytest
from PIL import Image

from mario.__main__ import SPRITES_FOLDER
from mario.constants.animation import FIRST_WALK_FRAME, WALK_FRAME_COUNT
from mario.constants.level import SCREEN_HEIGHT_PIXELS, SCREEN_WIDTH_PIXELS
from mario.level.background_scenery import BackgroundScenery
from mario.simulation.attempt import Attempt
from mario.snapshots.world_snapshot import MarioPose, WorldSnapshot
from mario.view.sprite_library import SpriteLibrary
from mario.view.sprite_renderer import SpriteRenderer
from tests.game.helpers import HOLD_LEFT, HOLD_NOTHING, HOLD_RIGHT, HOLD_RIGHT_RUN, big_mario_attempt, build_level

CAPTURES_FOLDER = Path(__file__).resolve().parents[2] / "test_output" / "walk_animation"
# Wide enough that the run never reaches the level's end.
CAPTURE_LEVEL_WIDTH_TILES = 400

# What he does, in order, and for how many ticks.
STAND_TICKS = 20
WALK_TICKS = 120
LET_GO_TICKS = 40
RUN_TICKS = 150
TURN_TICKS = 40

# The part of the screen around him that is captured, in screen pixels, its
# bottom a little under his feet so the ground shows, and how much it is enlarged.
CROP_WIDTH_PIXELS = 48
CROP_HEIGHT_PIXELS = 48
CROP_BELOW_FEET_PIXELS = 8
GIF_SCALE = 4
# GIF delays are whole hundredths of a second, and browsers slow anything under
# 2 of them, so each tick shows for 20 ms: the GIF plays at 5/6 of real time.
GIF_TICK_MILLISECONDS = 20

# The strip: consecutive ticks, one cell each, with his frame named under it.
STRIP_TICKS = 24
STRIP_CELL_WIDTH_PIXELS = 24
STRIP_SCALE = 3
STRIP_LABEL_HEIGHT_PIXELS = 18
STRIP_ROW_TITLE_WIDTH_PIXELS = 150
STRIP_FONT_SIZE = 18
STRIP_BACKGROUND_COLOUR = (255, 255, 255)
STRIP_TEXT_COLOUR = (0, 0, 0)

ALL_WALK_FRAMES = set(range(FIRST_WALK_FRAME, FIRST_WALK_FRAME + WALK_FRAME_COUNT))
# Under a tick that isn't a walking frame, the pose's letter.
POSE_LETTERS = {MarioPose.STANDING: "S", MarioPose.SKIDDING: "K", MarioPose.JUMPING: "J", MarioPose.CROUCHING: "C"}


@dataclass(frozen=True)
class CapturedTick:
    snapshot: WorldSnapshot
    picture: pygame.Surface        # the crop around him, at screen size


@dataclass(frozen=True)
class Phase:
    name: str
    buttons: int
    ticks: int


PHASES = (
    Phase("stand", HOLD_NOTHING, STAND_TICKS),
    Phase("walk", HOLD_RIGHT, WALK_TICKS),
    Phase("let go", HOLD_NOTHING, LET_GO_TICKS),
    Phase("run", HOLD_RIGHT_RUN, RUN_TICKS),
    Phase("turn", HOLD_LEFT, TURN_TICKS),
    Phase("stop", HOLD_NOTHING, LET_GO_TICKS),
)


def crop_around_mario(screen: pygame.Surface, snapshot: WorldSnapshot) -> pygame.Surface:
    mario = snapshot.mario
    centre_x = mario.x_pixels - snapshot.screen_left_x_pixels + mario.width_pixels // 2
    bottom_y = mario.y_pixels + mario.height_pixels + CROP_BELOW_FEET_PIXELS
    crop = pygame.Rect(centre_x - CROP_WIDTH_PIXELS // 2, bottom_y - CROP_HEIGHT_PIXELS,
                       CROP_WIDTH_PIXELS, CROP_HEIGHT_PIXELS)
    return screen.subsurface(crop.clip(screen.get_rect())).copy()


def capture(attempt: Attempt, renderer: SpriteRenderer) -> dict[str, list[CapturedTick]]:
    """Every phase played in turn, each tick drawn by the Sprite view."""
    screen = pygame.Surface((SCREEN_WIDTH_PIXELS, SCREEN_HEIGHT_PIXELS))
    captured = {}
    for phase in PHASES:
        ticks = []
        for _ in range(phase.ticks):
            attempt.step(phase.buttons)
            snapshot = WorldSnapshot.of(attempt)
            renderer.draw(snapshot, screen)
            ticks.append(CapturedTick(snapshot, crop_around_mario(screen, snapshot)))
        captured[phase.name] = ticks
    return captured


def as_image(surface: pygame.Surface, scale: int) -> Image.Image:
    width, height = surface.get_size()
    enlarged = pygame.transform.scale(surface, (width * scale, height * scale))
    return Image.frombytes("RGB", enlarged.get_size(), pygame.image.tobytes(enlarged, "RGB"))


def write_gif(path: Path, captured: dict[str, list[CapturedTick]]) -> None:
    frames = [as_image(tick.picture, GIF_SCALE) for ticks in captured.values() for tick in ticks]
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=GIF_TICK_MILLISECONDS, loop=0)


def frame_label(tick: CapturedTick) -> str:
    mario = tick.snapshot.mario
    return str(mario.walk_frame) if mario.pose is MarioPose.WALKING else POSE_LETTERS[mario.pose]


def write_strip(path: Path, rows: dict[str, list[CapturedTick]]) -> None:
    """One row per title: its ticks side by side, each with his walking frame (or
    his pose's letter) under it."""
    pygame.font.init()
    font = pygame.font.Font(None, STRIP_FONT_SIZE)
    cell_width = STRIP_CELL_WIDTH_PIXELS * STRIP_SCALE
    cell_height = CROP_HEIGHT_PIXELS * STRIP_SCALE + STRIP_LABEL_HEIGHT_PIXELS
    strip = pygame.Surface((STRIP_ROW_TITLE_WIDTH_PIXELS + STRIP_TICKS * cell_width, len(rows) * cell_height))
    strip.fill(STRIP_BACKGROUND_COLOUR)
    for row_index, (title, ticks) in enumerate(rows.items()):
        top = row_index * cell_height
        strip.blit(font.render(title, True, STRIP_TEXT_COLOUR), (0, top + cell_height // 2))
        for column, tick in enumerate(ticks[:STRIP_TICKS]):
            left = STRIP_ROW_TITLE_WIDTH_PIXELS + column * cell_width
            picture = tick.picture
            middle = pygame.Rect((picture.get_width() - STRIP_CELL_WIDTH_PIXELS) // 2, 0,
                                 STRIP_CELL_WIDTH_PIXELS, picture.get_height())
            cell = pygame.transform.scale(picture.subsurface(middle), (cell_width, middle.height * STRIP_SCALE))
            strip.blit(cell, (left, top))
            label = font.render(frame_label(tick), True, STRIP_TEXT_COLOUR)
            strip.blit(label, (left + cell_width // 2, top + cell_height - STRIP_LABEL_HEIGHT_PIXELS))
    pygame.image.save(strip, str(path))


@pytest.fixture(scope="module")
def renderer() -> SpriteRenderer:
    open_sky = BackgroundScenery([])
    return SpriteRenderer(SpriteLibrary.load(SPRITES_FOLDER), open_sky)


def test_the_knight_walking_and_running_is_captured_to_watch(renderer):
    level = build_level(width_tiles=CAPTURE_LEVEL_WIDTH_TILES)
    CAPTURES_FOLDER.mkdir(parents=True, exist_ok=True)
    strip_rows = {}
    for size, attempt in (("small", Attempt(level)), ("big", big_mario_attempt(level))):
        captured = capture(attempt, renderer)
        for phase_name in ("walk", "run"):
            walking_frames = {tick.snapshot.mario.walk_frame for tick in captured[phase_name]
                              if tick.snapshot.mario.pose is MarioPose.WALKING}
            assert walking_frames == ALL_WALK_FRAMES
        write_gif(CAPTURES_FOLDER / f"knight_walk_{size}.gif", captured)
        strip_rows[f"{size}: starts walking"] = captured["walk"]
        strip_rows[f"{size}: walking"] = captured["walk"][-STRIP_TICKS:]
        strip_rows[f"{size}: running"] = captured["run"][-STRIP_TICKS:]
        strip_rows[f"{size}: lets go"] = captured["let go"]
    write_strip(CAPTURES_FOLDER / "knight_walk_strip.png", strip_rows)
    assert (CAPTURES_FOLDER / "knight_walk_strip.png").exists()
