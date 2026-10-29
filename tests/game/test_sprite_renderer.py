"""The Sprite view (spec sections 8 and 12): every thing drawn from assets/sprites/
at the original's sizes, over the background scenery; a thing whose PNG is
missing is drawn in its hitbox colour instead, so the view works with an empty
folder and a PNG dropped in later shows with no code change."""

from dataclasses import replace
from pathlib import Path

import pygame
import pytest

from mario.__main__ import SPRITES_FOLDER
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
    FLAG_COLOUR,
    GOOMBA_COLOUR,
    GROUND_COLOUR,
    HILL_COLOUR,
    INVINCIBLE_MARIO_COLOUR,
    KOOPA_COLOUR,
    KOOPA_SHELL_COLOUR,
    MARIO_COLOUR,
    PIPE_COLOUR,
    SKY_COLOUR,
    SPRITE_SIZES,
    STARMAN_COLOUR,
    SUPER_MUSHROOM_COLOUR,
    USED_BLOCK_COLOUR,
)
from mario.level.background_scenery import BackgroundScenery
from mario.level.static_level import EnemyKind, StaticLevel
from mario.level.tile_kind import TileKind
from mario.simulation.attempt import Attempt
from mario.snapshots.world_snapshot import (
    AgentSnapshot,
    Area,
    BouncingBlockSnapshot,
    EnemySnapshot,
    FireballSnapshot,
    FlagSnapshot,
    HudSnapshot,
    ItemKind,
    ItemSnapshot,
    MarioPose,
    MarioSnapshot,
    PowerState,
    VisibleTiles,
    WorldSnapshot,
)
from mario.view.hitbox_colours import ENEMY_COLOURS, mario_colour
from mario.view.sprite_library import SpriteLibrary
from mario.view.sprite_renderer import SpriteRenderer

# The folder play mode reads its PNGs from, assets/sprites/.
SPRITES_README = SPRITES_FOLDER / "README.md"

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
               mario_is_invulnerable: bool = False, flag: FlagSnapshot | None = None,
               mario_is_invincible: bool = False, mario_faces_right: bool = True,
               ghosts: tuple[AgentSnapshot, ...] = ()) -> WorldSnapshot:
    """The level's start with only what is given on it; Mario out of sight below the screen unless placed."""
    return WorldSnapshot(tick=tick, screen_left_x_pixels=SKY_SCREEN_LEFT_X, tiles=tiles,
                         mario=MarioSnapshot(*mario_box, power_state, is_invulnerable=mario_is_invulnerable,
                                             is_invincible=mario_is_invincible, faces_right=mario_faces_right),
                         enemies=enemies, hud=HudSnapshot(0, 0, LEVEL_TIMER_START_UNITS),
                         items=items, fireballs=fireballs, flag=flag, ghosts=ghosts)


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


def goomba(is_defeated: bool = False, faces_right: bool = True) -> EnemySnapshot:
    return EnemySnapshot(EnemyKind.GOOMBA, THING_X, THING_Y, GOOMBA_HITBOX_WIDTH_PIXELS,
                         GOOMBA_HITBOX_HEIGHT_PIXELS, is_defeated, faces_right=faces_right)


def koopa(is_shell: bool = False, is_defeated: bool = False, faces_right: bool = True) -> EnemySnapshot:
    return EnemySnapshot(EnemyKind.KOOPA, THING_X, THING_Y, GOOMBA_HITBOX_WIDTH_PIXELS,
                         GOOMBA_HITBOX_HEIGHT_PIXELS, is_defeated, is_shell, faces_right)


def mushroom(is_emerging: bool = False, x: int = THING_X, y: int = THING_Y,
             kind: ItemKind = ItemKind.SUPER_MUSHROOM) -> ItemSnapshot:
    return ItemSnapshot(kind, x, y, ITEM_HITBOX_WIDTH_PIXELS, ITEM_HITBOX_HEIGHT_PIXELS, is_emerging)


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
    pytest.param(sky_screen(SMALL_MARIO_BOX, mario_is_invincible=True), INVINCIBLE_MARIO_COLOUR,
                 (MARIO_SPRITE_LEFT_X, MARIO_FEET_Y - 16, 16, 16), id="invincible small Mario"),
    pytest.param(sky_screen(BIG_MARIO_BOX, PowerState.FIERY, mario_is_invincible=True), INVINCIBLE_MARIO_COLOUR,
                 (MARIO_SPRITE_LEFT_X, MARIO_SPRITE_TOP_Y, 16, 32), id="invincible fire Mario"),
    pytest.param(sky_screen(enemies=(goomba(),)), GOOMBA_COLOUR, (THING_X, THING_Y, 16, 16), id="Goomba"),
    pytest.param(sky_screen(enemies=(goomba(is_defeated=True),)), GOOMBA_COLOUR,
                 (THING_X, THING_Y + 8, 16, 8), id="squashed Goomba"),
    # EnemyGraphicsTable: a Koopa fills the 16 x 24 enemy object; its shell, upright
    # or flipped, the lower 16 rows
    pytest.param(sky_screen(enemies=(koopa(),)), KOOPA_COLOUR, (THING_X, THING_Y - 8, 16, 24), id="Koopa"),
    pytest.param(sky_screen(enemies=(koopa(is_shell=True),)), KOOPA_SHELL_COLOUR, (THING_X, THING_Y, 16, 16),
                 id="Koopa shell"),
    pytest.param(sky_screen(enemies=(koopa(is_shell=True, is_defeated=True),)), KOOPA_SHELL_COLOUR,
                 (THING_X, THING_Y, 16, 16), id="defeated Koopa"),
    pytest.param(sky_screen(items=(mushroom(),)), SUPER_MUSHROOM_COLOUR, (THING_X, THING_Y, 16, 16),
                 id="Super Mushroom"),
    pytest.param(sky_screen(items=(mushroom(kind=ItemKind.STARMAN),)), STARMAN_COLOUR, (THING_X, THING_Y, 16, 16),
                 id="Starman"),
    pytest.param(sky_screen(fireballs=(fireball(is_exploding=False),)), FIREBALL_COLOUR,
                 (THING_X, THING_Y, 8, 8), id="fireball"),
    pytest.param(sky_screen(fireballs=(fireball(is_exploding=True),)), EXPLODING_FIREBALL_COLOUR,
                 (THING_X - 4, THING_Y - 4, 16, 16), id="fireball exploding"),
    # FlagpoleGfxHandler: three 8 x 8 sprites, two side by side from the flag's corner, one under the right
    pytest.param(sky_screen(flag=FlagSnapshot(THING_X, THING_Y)), FLAG_COLOUR, (THING_X, THING_Y, 16, 16),
                 id="flag"),
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


def test_a_flag_png_is_drawn_on_the_flag(tmp_path, scenery):
    write_png(tmp_path / "flag.png", (*PNG_COLOUR, 255))
    snapshot = sky_screen(flag=FlagSnapshot(THING_X, THING_Y))
    screen = drawn(renderer_with(tmp_path, scenery), snapshot)
    assert filled_box(screen, snapshot, (THING_X, THING_Y, 16, 16)) == {PNG_COLOUR}


def test_a_tile_or_scenery_png_is_drawn_on_every_tile_of_its_kind(tmp_path, world_1_1, scenery):
    write_png(tmp_path / "ground.png", (*PNG_COLOUR, 255))
    write_png(tmp_path / "cloud_top_left.png", (0, 255, 255, 255))
    snapshot = WorldSnapshot.of(Attempt(world_1_1))
    screen = drawn(renderer_with(tmp_path, scenery), snapshot)
    assert {colour_at(screen, snapshot, *tile_centre(column, 14)) for column in range(16)} == {PNG_COLOUR}
    assert colour_at(screen, snapshot, *tile_centre(8, 3)) == (0, 255, 255)
    assert colour_at(screen, snapshot, *tile_centre(2, 10)) == HILL_COLOUR    # no hill PNGs: still its colour


def test_a_hill_tile_is_drawn_with_the_picture_its_place_in_the_hill_picks(tmp_path, world_1_1, scenery):
    """The big hill's peak is (2, 10), its left slope under it at (1, 11)."""
    write_png(tmp_path / "hill_peak.png", (*PNG_COLOUR, 255))
    snapshot = WorldSnapshot.of(Attempt(world_1_1))
    screen = drawn(renderer_with(tmp_path, scenery), snapshot)
    assert colour_at(screen, snapshot, *tile_centre(2, 10)) == PNG_COLOUR
    assert colour_at(screen, snapshot, *tile_centre(1, 11)) == HILL_COLOUR    # no hill_left_slope.png


def test_a_cloud_tile_is_drawn_with_the_picture_its_place_in_the_cloud_picks(tmp_path, world_1_1, scenery):
    """The opening screen's cloud is columns 8-10 of rows 3 and 4: (9, 4) is its bottom middle."""
    write_png(tmp_path / "cloud_bottom_middle.png", (*PNG_COLOUR, 255))
    snapshot = WorldSnapshot.of(Attempt(world_1_1))
    screen = drawn(renderer_with(tmp_path, scenery), snapshot)
    assert colour_at(screen, snapshot, *tile_centre(9, 4)) == PNG_COLOUR
    assert colour_at(screen, snapshot, *tile_centre(9, 3)) == CLOUD_COLOUR    # no cloud_top_middle.png


def test_a_bush_tile_is_drawn_with_the_picture_its_place_in_the_bush_picks(tmp_path, world_1_1, scenery):
    """The opening screen's bush is columns 11-15 of row 12: (11, 12) is its left end."""
    write_png(tmp_path / "bush_left_end.png", (*PNG_COLOUR, 255))
    snapshot = WorldSnapshot.of(Attempt(world_1_1))
    screen = drawn(renderer_with(tmp_path, scenery), snapshot)
    assert colour_at(screen, snapshot, *tile_centre(11, 12)) == PNG_COLOUR
    assert colour_at(screen, snapshot, *tile_centre(12, 12)) == BUSH_COLOUR    # no bush_middle.png


def test_a_castle_tile_is_drawn_with_the_picture_its_place_in_the_castle_picks(tmp_path, world_1_1, scenery):
    """Under the tower, (204, 10) is the wall top; the wall's left edge at (202, 11)
    and the battlement's right corner merlon at (206, 10) have no PNG, so they fill in
    the castle's colour."""
    write_png(tmp_path / "castle_wall_top.png", (*PNG_COLOUR, 255))
    snapshot = level_screen(world_1_1, first_column=SCROLL_STOP_COLUMN)
    screen = drawn(renderer_with(tmp_path, scenery), snapshot)
    assert colour_at(screen, snapshot, *tile_centre(204, 10)) == PNG_COLOUR
    assert colour_at(screen, snapshot, *tile_centre(202, 11)) == CASTLE_BRICK_COLOUR
    assert colour_at(screen, snapshot, *tile_centre(206, 10)) == CASTLE_BRICK_COLOUR


def test_a_pipe_tile_is_drawn_with_the_picture_its_place_in_the_pipe_picks(tmp_path, world_1_1, scenery):
    """World 1-1's first pipe is columns 28-29 of rows 11-12: (28, 11) is its rim's
    left half; its rim's right half (29, 11) and its body (28, 12) have no PNG, so
    they fill in the pipe's colour."""
    write_png(tmp_path / "pipe_rim_left.png", (*PNG_COLOUR, 255))
    snapshot = level_screen(world_1_1, first_column=20)
    screen = drawn(renderer_with(tmp_path, scenery), snapshot)
    assert colour_at(screen, snapshot, *tile_centre(28, 11)) == PNG_COLOUR
    assert colour_at(screen, snapshot, *tile_centre(29, 11)) == PIPE_COLOUR
    assert colour_at(screen, snapshot, *tile_centre(28, 12)) == PIPE_COLOUR


# --- Facing: a sprite is drawn facing right, mirrored for a thing facing left (#56) --------

OTHER_PNG_COLOUR = (0, 255, 255)
GOOMBA_BOX = (THING_X, THING_Y, GOOMBA_HITBOX_WIDTH_PIXELS, GOOMBA_HITBOX_HEIGHT_PIXELS)


def write_two_tone_png(path: Path, size: tuple[int, int]) -> None:
    """A sprite whose left half is PNG_COLOUR and right half OTHER_PNG_COLOUR, so its mirror image shows."""
    width, height = size
    image = pygame.Surface(size, pygame.SRCALPHA)
    image.fill((*PNG_COLOUR, 255), pygame.Rect(0, 0, width // 2, height))
    image.fill((*OTHER_PNG_COLOUR, 255), pygame.Rect(width // 2, 0, width - width // 2, height))
    pygame.image.save(image, str(path))


def standing_place(box: tuple[int, int, int, int], sprite_name: str) -> tuple[int, int, int, int]:
    """The sprite's place: on the box's bottom, centred across it."""
    left_x, top_y, box_width, box_height = box
    width, height = SPRITE_SIZES[sprite_name]
    return left_x + box_width // 2 - width // 2, top_y + box_height - height, width, height


def halves(box: tuple[int, int, int, int]) -> tuple[tuple[int, int, int, int], tuple[int, int, int, int]]:
    left_x, top_y, width, height = box
    return (left_x, top_y, width // 2, height), (left_x + width // 2, top_y, width - width // 2, height)


# Each thing, its sprite, its box, and whether its sprite is drawn mirrored.
THINGS_AND_WHETHER_THEY_ARE_MIRRORED = [
    pytest.param(sky_screen(SMALL_MARIO_BOX), "mario_small", SMALL_MARIO_BOX, False, id="mario facing right"),
    pytest.param(sky_screen(SMALL_MARIO_BOX, mario_faces_right=False), "mario_small", SMALL_MARIO_BOX, True,
                 id="mario facing left"),
    pytest.param(sky_screen(enemies=(goomba(),)), "goomba", GOOMBA_BOX, False, id="goomba walking right"),
    pytest.param(sky_screen(enemies=(goomba(faces_right=False),)), "goomba", GOOMBA_BOX, True,
                 id="goomba walking left"),
    pytest.param(sky_screen(enemies=(koopa(faces_right=False),)), "koopa", GOOMBA_BOX, True,
                 id="koopa walking left"),
    pytest.param(sky_screen(enemies=(koopa(is_shell=True, faces_right=False),)), "koopa_shell", GOOMBA_BOX, False,
                 id="shell moving left: not mirrored"),
]


@pytest.mark.parametrize("snapshot, sprite_name, box, is_mirrored", THINGS_AND_WHETHER_THEY_ARE_MIRRORED)
def test_a_thing_facing_left_is_drawn_with_its_sprite_mirrored_in_the_same_place(
        tmp_path, scenery, snapshot, sprite_name, box, is_mirrored):
    write_two_tone_png(tmp_path / f"{sprite_name}.png", SPRITE_SIZES[sprite_name])
    screen = drawn(renderer_with(tmp_path, scenery), snapshot)
    place = standing_place(box, sprite_name)
    left_half, right_half = halves(place)
    left_colour, right_colour = (OTHER_PNG_COLOUR, PNG_COLOUR) if is_mirrored else (PNG_COLOUR, OTHER_PNG_COLOUR)
    assert filled_box(screen, snapshot, left_half) == {left_colour}
    assert filled_box(screen, snapshot, right_half) == {right_colour}
    assert border_colours(screen, snapshot, place) == {SKY_COLOUR}


def test_a_ghost_facing_left_is_drawn_with_his_sprite_mirrored(tmp_path, scenery):
    """Translucent, so his left half shows the blend his right half shows facing right."""
    write_two_tone_png(tmp_path / "mario_small.png", SPRITE_SIZES["mario_small"])
    renderer = renderer_with(tmp_path, scenery)
    left_half, right_half = halves(standing_place(SMALL_MARIO_BOX, "mario_small"))

    def ghost_drawn(faces_right: bool) -> tuple[pygame.Surface, WorldSnapshot]:
        ghost = AgentSnapshot(1, MarioSnapshot(*SMALL_MARIO_BOX, faces_right=faces_right), Area.LEVEL, True, False, SMALL_MARIO_BOX[0])
        snapshot = sky_screen(ghosts=(ghost,))
        return drawn(renderer, snapshot), snapshot

    facing_right, facing_left = ghost_drawn(faces_right=True), ghost_drawn(faces_right=False)
    assert filled_box(*facing_left, left_half) == filled_box(*facing_right, right_half)
    assert filled_box(*facing_left, right_half) == filled_box(*facing_right, left_half)
    assert filled_box(*facing_left, left_half) != filled_box(*facing_left, right_half)


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
    SpriteLibrary.load(SPRITES_FOLDER)


# --- Animation frames (#57) ------------------------------------------------------------------

FRAME_PNG_COLOUR = PNG_COLOUR
STANDING_PNG_COLOUR = OTHER_PNG_COLOUR


def with_mario_frame(snapshot: WorldSnapshot, pose: MarioPose, walk_frame: int = 1) -> WorldSnapshot:
    return WorldSnapshot(**{**vars(snapshot), "mario": replace(snapshot.mario, pose=pose, walk_frame=walk_frame)})


def box_of(mario: MarioSnapshot) -> tuple[int, int, int, int]:
    return mario.x_pixels, mario.y_pixels, mario.width_pixels, mario.height_pixels


@pytest.mark.parametrize("snapshot, standing_sprite_name, frame_sprite_name", [
    pytest.param(with_mario_frame(sky_screen(SMALL_MARIO_BOX), MarioPose.WALKING, 2),
                 "mario_small", "mario_small_walk_2", id="small Mario walking"),
    pytest.param(with_mario_frame(sky_screen(BIG_MARIO_BOX, PowerState.BIG), MarioPose.WALKING, 3),
                 "mario_big", "mario_big_walk_3", id="big Mario walking"),
    pytest.param(with_mario_frame(sky_screen(BIG_MARIO_BOX, PowerState.BIG), MarioPose.SKIDDING),
                 "mario_big", "mario_big_skid", id="big Mario skidding"),
    pytest.param(with_mario_frame(sky_screen(BIG_MARIO_BOX, PowerState.FIERY), MarioPose.JUMPING),
                 "mario_fiery", "mario_fiery_jump", id="fire Mario jumping"),
    pytest.param(with_mario_frame(sky_screen(SMALL_MARIO_BOX, PowerState.BIG), MarioPose.CROUCHING),
                 "mario_big", "mario_big_crouch", id="big Mario crouching, in small Mario's box"),
    pytest.param(with_mario_frame(sky_screen(SMALL_MARIO_BOX, mario_is_invincible=True), MarioPose.WALKING, 1),
                 "mario_small_invincible", "mario_small_invincible_walk_1", id="invincible small Mario walking"),
    pytest.param(with_mario_frame(sky_screen(BIG_MARIO_BOX, PowerState.FIERY, mario_is_invincible=True),
                                  MarioPose.JUMPING),
                 "mario_big_invincible", "mario_big_invincible_jump", id="invincible fire Mario jumping"),
])
def test_mario_is_drawn_with_the_frame_his_snapshot_names_else_standing_else_in_his_colour(
        tmp_path, scenery, snapshot, standing_sprite_name, frame_sprite_name):
    """At the frame's own size, standing on his box's bottom: the crouch is 16 x 24."""
    mario_box = box_of(snapshot.mario)
    frame_place = standing_place(mario_box, frame_sprite_name)
    standing_sprite_place = standing_place(mario_box, standing_sprite_name)
    write_png(tmp_path / f"{frame_sprite_name}.png", (*FRAME_PNG_COLOUR, 255))
    write_png(tmp_path / f"{standing_sprite_name}.png", (*STANDING_PNG_COLOUR, 255))
    screen = drawn(renderer_with(tmp_path, scenery), snapshot)
    assert filled_box(screen, snapshot, frame_place) == {FRAME_PNG_COLOUR}
    assert border_colours(screen, snapshot, frame_place) == {SKY_COLOUR}

    (tmp_path / f"{frame_sprite_name}.png").unlink()
    screen = drawn(renderer_with(tmp_path, scenery), snapshot)
    assert filled_box(screen, snapshot, standing_sprite_place) == {STANDING_PNG_COLOUR}

    (tmp_path / f"{standing_sprite_name}.png").unlink()
    screen = drawn(renderer_with(tmp_path, scenery), snapshot)
    assert filled_box(screen, snapshot, standing_sprite_place) == {mario_colour(snapshot.mario)}


def test_standing_mario_is_drawn_with_his_standing_sprite_whatever_frames_there_are(tmp_path, scenery):
    write_png(tmp_path / "mario_small.png", (*STANDING_PNG_COLOUR, 255))
    for frame_sprite_name in ("mario_small_walk_1", "mario_small_jump", "mario_small_skid"):
        write_png(tmp_path / f"{frame_sprite_name}.png", (*FRAME_PNG_COLOUR, 255))
    snapshot = with_mario_frame(sky_screen(SMALL_MARIO_BOX), MarioPose.STANDING)
    screen = drawn(renderer_with(tmp_path, scenery), snapshot)
    assert filled_box(screen, snapshot, standing_place(SMALL_MARIO_BOX, "mario_small")) == {STANDING_PNG_COLOUR}


def test_a_ghost_is_drawn_with_the_frame_his_mario_shows(tmp_path, scenery):
    """Translucent, so the jump frame's colour shows blended, unlike the standing sprite's."""
    write_png(tmp_path / "mario_small.png", (*STANDING_PNG_COLOUR, 255))
    write_png(tmp_path / "mario_small_jump.png", (*FRAME_PNG_COLOUR, 255))
    renderer = renderer_with(tmp_path, scenery)
    place = standing_place(SMALL_MARIO_BOX, "mario_small")

    def ghost_colours(pose: MarioPose) -> set[tuple[int, int, int]]:
        ghost = AgentSnapshot(1, MarioSnapshot(*SMALL_MARIO_BOX, pose=pose), Area.LEVEL, True, False, SMALL_MARIO_BOX[0])
        snapshot = sky_screen(ghosts=(ghost,))
        return filled_box(drawn(renderer, snapshot), snapshot, place)

    jumping, standing = ghost_colours(MarioPose.JUMPING), ghost_colours(MarioPose.STANDING)
    assert len(jumping) == 1 and len(standing) == 1 and jumping != standing


@pytest.mark.parametrize("enemy, sprite_place, standing_sprite_name, frame_sprite_name", [
    pytest.param(replace(goomba(), walk_frame=2), (THING_X, THING_Y, 16, 16), "goomba", "goomba_walk_2",
                 id="Goomba"),
    pytest.param(replace(koopa(), walk_frame=2), (THING_X, THING_Y - 8, 16, 24), "koopa", "koopa_walk_2",
                 id="Koopa"),
])
def test_a_walking_enemy_is_drawn_with_its_second_frame_else_its_own_sprite_else_its_colour(
        tmp_path, scenery, enemy, sprite_place, standing_sprite_name, frame_sprite_name):
    write_png(tmp_path / f"{frame_sprite_name}.png", (*FRAME_PNG_COLOUR, 255))
    write_png(tmp_path / f"{standing_sprite_name}.png", (*STANDING_PNG_COLOUR, 255))
    second_frame = sky_screen(enemies=(enemy,))
    first_frame = sky_screen(enemies=(replace(enemy, walk_frame=1),))
    assert filled_box(drawn(renderer_with(tmp_path, scenery), second_frame), second_frame,
                      sprite_place) == {FRAME_PNG_COLOUR}
    assert filled_box(drawn(renderer_with(tmp_path, scenery), first_frame), first_frame,
                      sprite_place) == {STANDING_PNG_COLOUR}

    (tmp_path / f"{frame_sprite_name}.png").unlink()
    assert filled_box(drawn(renderer_with(tmp_path, scenery), second_frame), second_frame,
                      sprite_place) == {STANDING_PNG_COLOUR}
    (tmp_path / f"{standing_sprite_name}.png").unlink()
    assert filled_box(drawn(renderer_with(tmp_path, scenery), second_frame), second_frame,
                      sprite_place) == {ENEMY_COLOURS[enemy.kind]}


@pytest.mark.parametrize("enemy, sprite_name, sprite_place", [
    pytest.param(replace(koopa(is_shell=True), walk_frame=2), "koopa_shell", (THING_X, THING_Y, 16, 16),
                 id="Koopa shell"),
    pytest.param(replace(goomba(is_defeated=True), walk_frame=2), "goomba_defeated", (THING_X, THING_Y + 8, 16, 8),
                 id="squashed Goomba"),
])
def test_a_shell_and_a_defeated_enemy_are_drawn_without_a_walking_frame(tmp_path, scenery, enemy, sprite_name,
                                                                        sprite_place):
    write_png(tmp_path / "goomba_walk_2.png", (*FRAME_PNG_COLOUR, 255))
    write_png(tmp_path / "koopa_walk_2.png", (*FRAME_PNG_COLOUR, 255))
    write_png(tmp_path / f"{sprite_name}.png", (*STANDING_PNG_COLOUR, 255))
    snapshot = sky_screen(enemies=(enemy,))
    assert filled_box(drawn(renderer_with(tmp_path, scenery), snapshot), snapshot,
                      sprite_place) == {STANDING_PNG_COLOUR}
