"""The Sprite view (spec sections 8 and 12): every thing drawn from assets/sprites/
at the original's sizes, over the background scenery; a thing whose PNG is
missing is drawn in its hitbox colour instead, so the view works with an empty
folder and a PNG dropped in later shows with no code change."""

from pathlib import Path

import pygame
import pytest

from mario.constants.level import (
    FIREBALL_SIZE_PIXELS,
    GOOMBA_HITBOX_HEIGHT_PIXELS,
    GOOMBA_HITBOX_WIDTH_PIXELS,
    ITEM_HITBOX_HEIGHT_PIXELS,
    ITEM_HITBOX_WIDTH_PIXELS,
    LEVEL_TIMER_START_UNITS,
    SCREEN_HEIGHT_PIXELS,
    SCREEN_WIDTH_PIXELS,
    SCROLL_STOP_COLUMN,
    TILE_SIZE_PIXELS,
)
from mario.constants.view import (
    BUSH_COLOUR,
    CASTLE_BRICK_COLOUR,
    CLOUD_COLOUR,
    EXPLODING_FIREBALL_COLOUR,
    FIREBALL_COLOUR,
    FIRE_MARIO_COLOUR,
    GOOMBA_COLOUR,
    GROUND_COLOUR,
    HILL_COLOUR,
    MARIO_COLOUR,
    SKY_COLOUR,
    SPRITE_SIZES,
    SUPER_MUSHROOM_COLOUR,
    USED_BLOCK_COLOUR,
)
from mario.level.background_scenery import BackgroundScenery
from mario.level.static_level import EnemyKind, StaticLevel
from mario.level.tile_kind import TileKind
from mario.simulation.attempt import Attempt
from mario.snapshots.world_snapshot import (
    BouncingBlockSnapshot,
    EnemySnapshot,
    FireballSnapshot,
    HudSnapshot,
    ItemKind,
    ItemSnapshot,
    MarioSnapshot,
    PowerState,
    VisibleTiles,
    WorldSnapshot,
)
from mario.view.sprite_library import SpriteLibrary
from mario.view.sprite_renderer import SpriteRenderer

REPO_ROOT = Path(__file__).parent.parent.parent
SPRITES_README = REPO_ROOT / "assets" / "sprites" / "README.md"

# A screen of open sky at the level's start, where things are put by hand.
SKY_SCREEN_LEFT_X = 0
THING_X, THING_Y = 72, 64                      # a box's top-left, in level pixels, in open sky
# Mario's boxes, from his 16 x 32 sprite at (THING_X - 2, MARIO_SPRITE_TOP_Y): small Mario's
# is 12 x 14 at sprite offset (2, 18), big Mario's 12 x 28 at (2, 4) (physics research).
MARIO_SPRITE_LEFT_X, MARIO_SPRITE_TOP_Y = THING_X - 2, 40
SMALL_MARIO_BOX = (THING_X, MARIO_SPRITE_TOP_Y + 18, 12, 14)
BIG_MARIO_BOX = (THING_X, MARIO_SPRITE_TOP_Y + 4, 12, 28)
MARIO_FEET_Y = MARIO_SPRITE_TOP_Y + 32


@pytest.fixture(scope="module")
def scenery() -> BackgroundScenery:
    return BackgroundScenery.load_world_1_1()


def renderer_with(sprites_folder: Path, scenery: BackgroundScenery) -> SpriteRenderer:
    return SpriteRenderer(SpriteLibrary.load(sprites_folder), scenery)


def drawn(renderer: SpriteRenderer, snapshot: WorldSnapshot) -> pygame.Surface:
    screen = pygame.Surface((SCREEN_WIDTH_PIXELS, SCREEN_HEIGHT_PIXELS))
    renderer.draw(snapshot, screen)
    return screen


def colour_at(screen: pygame.Surface, snapshot: WorldSnapshot, level_x: int, y: int) -> tuple[int, int, int]:
    return tuple(screen.get_at((level_x - snapshot.screen_left_x_pixels, y)))[:3]


def tile_centre(column: int, row: int) -> tuple[int, int]:
    """The level pixel in the middle of the tile."""
    return column * TILE_SIZE_PIXELS + TILE_SIZE_PIXELS // 2, row * TILE_SIZE_PIXELS + TILE_SIZE_PIXELS // 2


def level_screen(level: StaticLevel, first_column: int, tick: int = 0,
                 bouncing_blocks: tuple[BouncingBlockSnapshot, ...] = ()) -> WorldSnapshot:
    """The level's own tiles with the screen's left edge at the column, Mario out of sight below it."""
    rows = tuple(tuple(level.tile_kind(column, row) for column in range(first_column, first_column + 17))
                 for row in range(level.height_tiles))
    return WorldSnapshot(tick=tick, screen_left_x_pixels=first_column * TILE_SIZE_PIXELS,
                         tiles=VisibleTiles(first_column, rows),
                         mario=MarioSnapshot(first_column * TILE_SIZE_PIXELS, SCREEN_HEIGHT_PIXELS, 12, 14),
                         enemies=(), hud=HudSnapshot(0, 0, LEVEL_TIMER_START_UNITS),
                         bouncing_blocks=bouncing_blocks)


def sky_screen(mario_box: tuple[int, int, int, int] = (0, SCREEN_HEIGHT_PIXELS, 12, 14),
               power_state: PowerState = PowerState.SMALL, enemies: tuple[EnemySnapshot, ...] = (),
               items: tuple[ItemSnapshot, ...] = (), fireballs: tuple[FireballSnapshot, ...] = (),
               tiles: VisibleTiles = VisibleTiles(0, ()), tick: int = 0,
               mario_is_invulnerable: bool = False) -> WorldSnapshot:
    """The level's start with only what is given on it; Mario out of sight below the screen unless placed."""
    return WorldSnapshot(tick=tick, screen_left_x_pixels=SKY_SCREEN_LEFT_X, tiles=tiles,
                         mario=MarioSnapshot(*mario_box, power_state, is_invulnerable=mario_is_invulnerable),
                         enemies=enemies, hud=HudSnapshot(0, 0, LEVEL_TIMER_START_UNITS),
                         items=items, fireballs=fireballs)


def filled_box(screen: pygame.Surface, snapshot: WorldSnapshot,
               box: tuple[int, int, int, int]) -> set[tuple[int, int, int]]:
    """The colours inside the box, given in level pixels."""
    left_x, top_y, width, height = box
    return {colour_at(screen, snapshot, x, y) for x in range(left_x, left_x + width)
            for y in range(top_y, top_y + height)}


def border_colours(screen: pygame.Surface, snapshot: WorldSnapshot,
                   box: tuple[int, int, int, int]) -> set[tuple[int, int, int]]:
    """The colours of the ring of pixels just outside the box."""
    left_x, top_y, width, height = box
    ring = ([(x, top_y - 1) for x in range(left_x - 1, left_x + width + 1)]
            + [(x, top_y + height) for x in range(left_x - 1, left_x + width + 1)]
            + [(left_x - 1, y) for y in range(top_y, top_y + height)]
            + [(left_x + width, y) for y in range(top_y, top_y + height)])
    return {colour_at(screen, snapshot, x, y) for x, y in ring}


def write_png(path: Path, colour: tuple[int, int, int, int], size: tuple[int, int] = (4, 4)) -> None:
    image = pygame.Surface(size, pygame.SRCALPHA)
    image.fill(colour)
    pygame.image.save(image, str(path))


# --- With an empty assets/sprites/ -----------------------------------------------------------


def test_with_no_sprites_the_opening_screen_shows_the_level_and_its_scenery_in_their_colours(
        tmp_path, world_1_1, scenery):
    snapshot = WorldSnapshot.of(Attempt(world_1_1))
    screen = drawn(renderer_with(tmp_path, scenery), snapshot)
    assert colour_at(screen, snapshot, *tile_centre(0, 13)) == GROUND_COLOUR
    assert colour_at(screen, snapshot, *tile_centre(8, 3)) == CLOUD_COLOUR
    assert colour_at(screen, snapshot, *tile_centre(2, 10)) == HILL_COLOUR
    assert colour_at(screen, snapshot, *tile_centre(11, 12)) == BUSH_COLOUR
    assert colour_at(screen, snapshot, *tile_centre(0, 2)) == SKY_COLOUR


def test_the_hidden_block_and_the_castle_stopper_are_not_drawn(tmp_path, world_1_1, scenery):
    renderer = renderer_with(tmp_path, scenery)
    hidden_block_screen = level_screen(world_1_1, first_column=56)
    assert colour_at(drawn(renderer, hidden_block_screen), hidden_block_screen, *tile_centre(64, 8)) == SKY_COLOUR
    castle_screen = level_screen(world_1_1, first_column=SCROLL_STOP_COLUMN)
    assert colour_at(drawn(renderer, castle_screen), castle_screen, *tile_centre(205, 12)) == CASTLE_BRICK_COLOUR


def goomba(is_defeated: bool = False) -> EnemySnapshot:
    return EnemySnapshot(EnemyKind.GOOMBA, THING_X, THING_Y, GOOMBA_HITBOX_WIDTH_PIXELS,
                         GOOMBA_HITBOX_HEIGHT_PIXELS, is_defeated)


def mushroom(is_emerging: bool = False, x: int = THING_X, y: int = THING_Y) -> ItemSnapshot:
    return ItemSnapshot(ItemKind.SUPER_MUSHROOM, x, y, ITEM_HITBOX_WIDTH_PIXELS, ITEM_HITBOX_HEIGHT_PIXELS,
                        is_emerging)


def fireball(is_exploding: bool) -> FireballSnapshot:
    return FireballSnapshot(THING_X, THING_Y, FIREBALL_SIZE_PIXELS, FIREBALL_SIZE_PIXELS, is_exploding)


# Each thing, and the place its sprite takes at the original's size: standing on
# its box's bottom, centred across it; a fireball's explosion centred on it
# (DrawExplosion_Fireball: four 8 x 8 sprites from 4 px up and left of it).
THINGS_AND_THEIR_SPRITES_PLACES = [
    pytest.param(sky_screen(SMALL_MARIO_BOX), MARIO_COLOUR,
                 (MARIO_SPRITE_LEFT_X, MARIO_FEET_Y - 16, 16, 16), id="small Mario"),
    pytest.param(sky_screen(BIG_MARIO_BOX, PowerState.BIG), MARIO_COLOUR,
                 (MARIO_SPRITE_LEFT_X, MARIO_SPRITE_TOP_Y, 16, 32), id="big Mario"),
    pytest.param(sky_screen(BIG_MARIO_BOX, PowerState.FIERY), FIRE_MARIO_COLOUR,
                 (MARIO_SPRITE_LEFT_X, MARIO_SPRITE_TOP_Y, 16, 32), id="fire Mario"),
    pytest.param(sky_screen(enemies=(goomba(),)), GOOMBA_COLOUR, (THING_X, THING_Y, 16, 16), id="Goomba"),
    pytest.param(sky_screen(enemies=(goomba(is_defeated=True),)), GOOMBA_COLOUR,
                 (THING_X, THING_Y + 8, 16, 8), id="squashed Goomba"),
    pytest.param(sky_screen(items=(mushroom(),)), SUPER_MUSHROOM_COLOUR, (THING_X, THING_Y, 16, 16),
                 id="Super Mushroom"),
    pytest.param(sky_screen(fireballs=(fireball(is_exploding=False),)), FIREBALL_COLOUR,
                 (THING_X, THING_Y, 8, 8), id="fireball"),
    pytest.param(sky_screen(fireballs=(fireball(is_exploding=True),)), EXPLODING_FIREBALL_COLOUR,
                 (THING_X - 4, THING_Y - 4, 16, 16), id="fireball exploding"),
]


@pytest.mark.parametrize("snapshot, hitbox_colour, sprite_place", THINGS_AND_THEIR_SPRITES_PLACES)
def test_with_no_sprites_each_thing_fills_its_sprites_place_in_its_hitbox_colour(
        tmp_path, scenery, snapshot, hitbox_colour, sprite_place):
    screen = drawn(renderer_with(tmp_path, scenery), snapshot)
    assert filled_box(screen, snapshot, sprite_place) == {hitbox_colour}
    assert border_colours(screen, snapshot, sprite_place) == {SKY_COLOUR}


def test_a_rising_item_is_drawn_behind_its_block_and_a_bumped_block_raised(tmp_path, scenery):
    """Half risen: the mushroom's top half shows above the block, its bottom half is hidden in it."""
    block_column, block_row = THING_X // TILE_SIZE_PIXELS, THING_Y // TILE_SIZE_PIXELS
    block_x, block_y = block_column * TILE_SIZE_PIXELS, block_row * TILE_SIZE_PIXELS
    rows = tuple(tuple(TileKind.USED_BLOCK if (column, row) == (block_column, block_row) else TileKind.EMPTY
                       for column in range(block_column + 1)) for row in range(block_row + 1))
    snapshot = sky_screen(items=(mushroom(is_emerging=True, x=block_x, y=block_y - TILE_SIZE_PIXELS // 2),),
                          tiles=VisibleTiles(0, rows))
    screen = drawn(renderer_with(tmp_path, scenery), snapshot)
    assert colour_at(screen, snapshot, block_x, block_y - 1) == SUPER_MUSHROOM_COLOUR
    assert colour_at(screen, snapshot, block_x, block_y) == USED_BLOCK_COLOUR
    bumped = WorldSnapshot(**{**vars(snapshot), "items": (),
                              "bouncing_blocks": (BouncingBlockSnapshot(block_column, block_row, -4),)})
    screen = drawn(renderer_with(tmp_path, scenery), bumped)
    assert colour_at(screen, bumped, block_x, block_y - 4) == USED_BLOCK_COLOUR
    assert colour_at(screen, bumped, block_x, block_y + TILE_SIZE_PIXELS - 4) == SKY_COLOUR


def test_invulnerable_mario_blinks_drawn_only_on_even_ticks(tmp_path, scenery):
    renderer = renderer_with(tmp_path, scenery)
    mario_x, mario_y = THING_X, SMALL_MARIO_BOX[1]
    for tick, is_invulnerable, colour in [(0, True, MARIO_COLOUR), (1, True, SKY_COLOUR), (1, False, MARIO_COLOUR)]:
        snapshot = sky_screen(SMALL_MARIO_BOX, tick=tick, mario_is_invulnerable=is_invulnerable)
        assert colour_at(drawn(renderer, snapshot), snapshot, mario_x, mario_y) == colour


# --- A PNG dropped into assets/sprites/ ----------------------------------------------------

PNG_COLOUR = (255, 0, 255)


def test_a_png_dropped_in_under_its_name_is_drawn_at_its_sprites_size_in_place_of_the_colour(tmp_path, scenery):
    write_png(tmp_path / "goomba_defeated.png", (*PNG_COLOUR, 255), size=(3, 5))
    snapshot = sky_screen(enemies=(goomba(is_defeated=True),))
    screen = drawn(renderer_with(tmp_path, scenery), snapshot)
    squashed_goombas_place = (THING_X, THING_Y + 8, 16, 8)
    assert filled_box(screen, snapshot, squashed_goombas_place) == {PNG_COLOUR}
    assert border_colours(screen, snapshot, squashed_goombas_place) == {SKY_COLOUR}


def test_a_tile_or_scenery_png_is_drawn_on_every_tile_of_its_kind(tmp_path, world_1_1, scenery):
    write_png(tmp_path / "ground.png", (*PNG_COLOUR, 255))
    write_png(tmp_path / "cloud.png", (0, 255, 255, 255))
    snapshot = WorldSnapshot.of(Attempt(world_1_1))
    screen = drawn(renderer_with(tmp_path, scenery), snapshot)
    assert {colour_at(screen, snapshot, *tile_centre(column, 14)) for column in range(16)} == {PNG_COLOUR}
    assert colour_at(screen, snapshot, *tile_centre(8, 3)) == (0, 255, 255)
    assert colour_at(screen, snapshot, *tile_centre(2, 10)) == HILL_COLOUR    # no hill.png: still its colour


def test_a_sprites_transparent_pixels_show_what_is_behind_it(tmp_path, scenery):
    write_png(tmp_path / "mario_small.png", (*PNG_COLOUR, 0))
    snapshot = sky_screen(SMALL_MARIO_BOX)
    screen = drawn(renderer_with(tmp_path, scenery), snapshot)
    assert filled_box(screen, snapshot, SMALL_MARIO_BOX) == {SKY_COLOUR}


def test_a_png_under_a_name_the_view_does_not_know_is_ignored(tmp_path, scenery):
    write_png(tmp_path / "goomba_walking.png", (*PNG_COLOUR, 255))
    snapshot = sky_screen(enemies=(goomba(),))
    screen = drawn(renderer_with(tmp_path, scenery), snapshot)
    assert filled_box(screen, snapshot, (THING_X, THING_Y, 16, 16)) == {GOOMBA_COLOUR}


def test_the_sprites_readme_documents_every_sprite_file_and_its_size():
    readme = SPRITES_README.read_text(encoding="utf8")
    for name, (width, height) in SPRITE_SIZES.items():
        assert f"`{name}.png` | {width} × {height}" in readme, name


def test_the_repos_sprites_folder_loads():
    """Whatever has been added so far, the folder the play mode reads loads."""
    SpriteLibrary.load(SPRITES_README.parent)
