"""The Sprite view: the level as humans see it, every thing drawn with its sprite
from assets/sprites/ at the original's size, over the background scenery.

A thing whose sprite is missing fills the sprite's place in its hitbox colour,
so the view works with an empty folder and a PNG dropped in later shows with
no code change (spec sections 8 and 12).
"""

import pygame

from mario.constants.level import TILE_SIZE_PIXELS
from mario.constants.view import (
    BUSH_COLOUR,
    CASTLE_BRICK_COLOUR,
    CASTLE_OPENING_COLOUR,
    CLOUD_COLOUR,
    EXPLODING_FIREBALL_COLOUR,
    FIREBALL_COLOUR,
    HILL_COLOUR,
    INVULNERABLE_MARIO_DRAWN_EVERY_TICKS,
    SKY_COLOUR,
    SPRITE_SIZES,
)
from mario.level.background_scenery import BackgroundScenery, SceneryKind
from mario.level.static_level import EnemyKind
from mario.level.tile_kind import TileKind
from mario.snapshots.world_snapshot import (
    EnemySnapshot,
    FireballSnapshot,
    ItemKind,
    ItemSnapshot,
    MarioSnapshot,
    PowerState,
    WorldSnapshot,
)
from mario.view.hitbox_colours import ENEMY_COLOURS, ITEM_COLOURS, MARIO_COLOURS, TILE_COLOURS
from mario.view.sprite_library import SpriteLibrary

# Tiles by how they look: a brick or ? block doesn't show what it holds. Tiles
# not listed aren't drawn: open sky, the hidden 1-UP block until it is hit, and
# the castle stopper behind the castle.
TILE_SPRITE_NAMES = {
    TileKind.GROUND: "ground",
    TileKind.HARD_BLOCK: "hard_block",
    TileKind.BRICK: "brick",
    TileKind.STARMAN_BRICK: "brick",
    TileKind.MULTI_COIN_BRICK: "brick",
    TileKind.COIN_QUESTION_BLOCK: "question_block",
    TileKind.POWER_UP_QUESTION_BLOCK: "question_block",
    TileKind.USED_BLOCK: "used_block",
    TileKind.PIPE: "pipe",
    TileKind.FLAGPOLE: "flagpole",
}

SCENERY_COLOURS = {
    SceneryKind.CLOUD: CLOUD_COLOUR,
    SceneryKind.HILL: HILL_COLOUR,
    SceneryKind.BUSH: BUSH_COLOUR,
    SceneryKind.CASTLE_BATTLEMENT: CASTLE_BRICK_COLOUR,
    SceneryKind.CASTLE_WINDOW: CASTLE_OPENING_COLOUR,
    SceneryKind.CASTLE_BRICK: CASTLE_BRICK_COLOUR,
    SceneryKind.CASTLE_DOOR_ARCH: CASTLE_BRICK_COLOUR,
    SceneryKind.CASTLE_DOOR: CASTLE_OPENING_COLOUR,
}

MARIO_SPRITE_NAMES = {
    PowerState.SMALL: "mario_small",
    PowerState.BIG: "mario_big",
    PowerState.FIERY: "mario_fiery",
}

ENEMY_SPRITE_NAMES = {
    EnemyKind.GOOMBA: "goomba",
}

DEFEATED_ENEMY_SPRITE_NAMES = {
    EnemyKind.GOOMBA: "goomba_defeated",
}

ITEM_SPRITE_NAMES = {
    ItemKind.SUPER_MUSHROOM: "super_mushroom",
    ItemKind.ONE_UP_MUSHROOM: "one_up_mushroom",
    ItemKind.FIRE_FLOWER: "fire_flower",
}

FIREBALL_SPRITE_NAME = "fireball"
FIREBALL_EXPLOSION_SPRITE_NAME = "fireball_explosion"


class SpriteRenderer:
    def __init__(self, sprites: SpriteLibrary, scenery: BackgroundScenery):
        self._sprites = sprites
        self._scenery = scenery

    def draw(self, snapshot: WorldSnapshot, screen: pygame.Surface) -> None:
        """Scenery behind the tiles, as in the original; items still rising out of
        their block behind it too."""
        screen.fill(SKY_COLOUR)
        self._draw_scenery(snapshot, screen)
        for item in snapshot.items:
            if item.is_emerging:
                self._draw_item(item, snapshot.screen_left_x_pixels, screen)
        self._draw_tiles(snapshot, screen)
        for item in snapshot.items:
            if not item.is_emerging:
                self._draw_item(item, snapshot.screen_left_x_pixels, screen)
        for enemy in snapshot.enemies:
            self._draw_enemy(enemy, snapshot.screen_left_x_pixels, screen)
        for fireball in snapshot.fireballs:
            self._draw_fireball(fireball, snapshot.screen_left_x_pixels, screen)
        mario = snapshot.mario
        if not mario.is_invulnerable or snapshot.tick % INVULNERABLE_MARIO_DRAWN_EVERY_TICKS == 0:
            self._draw_mario(mario, snapshot.screen_left_x_pixels, screen)

    def _draw_scenery(self, snapshot: WorldSnapshot, screen: pygame.Surface) -> None:
        """Behind every tile the screen shows; each SceneryKind's value is its sprite name."""
        tiles = snapshot.tiles
        for row, kinds in enumerate(tiles.rows):
            for column in range(tiles.first_column, tiles.first_column + len(kinds)):
                scenery_kind = self._scenery.scenery_kind(column, row)
                if scenery_kind is not None:
                    sprite_name = scenery_kind.value
                    self._draw_sprite(sprite_name, SCENERY_COLOURS[scenery_kind],
                                      _standing_on(_tile_box(column, row), sprite_name),
                                      snapshot.screen_left_x_pixels, screen)

    def _draw_tiles(self, snapshot: WorldSnapshot, screen: pygame.Surface) -> None:
        """Every tile in its place, a bouncing block raised above it."""
        tiles = snapshot.tiles
        bounce_offsets = {(block.column, block.row): block.offset_y_pixels for block in snapshot.bouncing_blocks}
        for row, kinds in enumerate(tiles.rows):
            for column_offset, kind in enumerate(kinds):
                sprite_name = TILE_SPRITE_NAMES.get(kind)
                if sprite_name is None:
                    continue
                column = tiles.first_column + column_offset
                tile_box = _tile_box(column, row).move(0, bounce_offsets.get((column, row), 0))
                self._draw_sprite(sprite_name, TILE_COLOURS[kind], _standing_on(tile_box, sprite_name),
                                  snapshot.screen_left_x_pixels, screen)

    def _draw_mario(self, mario: MarioSnapshot, screen_left_x_pixels: int, screen: pygame.Surface) -> None:
        sprite_name = MARIO_SPRITE_NAMES[mario.power_state]
        box = _hitbox(mario)
        self._draw_sprite(sprite_name, MARIO_COLOURS[mario.power_state], _standing_on(box, sprite_name),
                          screen_left_x_pixels, screen)

    def _draw_enemy(self, enemy: EnemySnapshot, screen_left_x_pixels: int, screen: pygame.Surface) -> None:
        sprite_names = DEFEATED_ENEMY_SPRITE_NAMES if enemy.is_defeated else ENEMY_SPRITE_NAMES
        sprite_name = sprite_names[enemy.kind]
        box = _hitbox(enemy)
        self._draw_sprite(sprite_name, ENEMY_COLOURS[enemy.kind], _standing_on(box, sprite_name),
                          screen_left_x_pixels, screen)

    def _draw_item(self, item: ItemSnapshot, screen_left_x_pixels: int, screen: pygame.Surface) -> None:
        sprite_name = ITEM_SPRITE_NAMES[item.kind]
        box = _hitbox(item)
        self._draw_sprite(sprite_name, ITEM_COLOURS[item.kind], _standing_on(box, sprite_name),
                          screen_left_x_pixels, screen)

    def _draw_fireball(self, fireball: FireballSnapshot, screen_left_x_pixels: int, screen: pygame.Surface) -> None:
        """Its explosion is centred on it (DrawExplosion_Fireball)."""
        box = _hitbox(fireball)
        if fireball.is_exploding:
            self._draw_sprite(FIREBALL_EXPLOSION_SPRITE_NAME, EXPLODING_FIREBALL_COLOUR,
                              _centred_on(box, FIREBALL_EXPLOSION_SPRITE_NAME), screen_left_x_pixels, screen)
        else:
            self._draw_sprite(FIREBALL_SPRITE_NAME, FIREBALL_COLOUR, _standing_on(box, FIREBALL_SPRITE_NAME),
                              screen_left_x_pixels, screen)

    def _draw_sprite(self, sprite_name: str, hitbox_colour: tuple[int, int, int], place: pygame.Rect,
                     screen_left_x_pixels: int, screen: pygame.Surface) -> None:
        """The sprite in its place, given in level pixels; while it is missing, its place in the colour."""
        place_on_screen = place.move(-screen_left_x_pixels, 0)
        sprite = self._sprites.sprite(sprite_name)
        if sprite is None:
            screen.fill(hitbox_colour, place_on_screen)
        else:
            screen.blit(sprite, place_on_screen)


def _hitbox(thing: MarioSnapshot | EnemySnapshot | ItemSnapshot | FireballSnapshot) -> pygame.Rect:
    """The thing's box in level pixels."""
    return pygame.Rect(thing.x_pixels, thing.y_pixels, thing.width_pixels, thing.height_pixels)


def _tile_box(column: int, row: int) -> pygame.Rect:
    return pygame.Rect(column * TILE_SIZE_PIXELS, row * TILE_SIZE_PIXELS, TILE_SIZE_PIXELS, TILE_SIZE_PIXELS)


def _standing_on(box: pygame.Rect, sprite_name: str) -> pygame.Rect:
    """The sprite's place at its size: on the box's bottom, centred across it, as
    the original's sprites stand on their feet (Mario's 16 px sprite is 2 px either
    side of his 12 px box)."""
    width, height = SPRITE_SIZES[sprite_name]
    return pygame.Rect(box.centerx - width // 2, box.bottom - height, width, height)


def _centred_on(box: pygame.Rect, sprite_name: str) -> pygame.Rect:
    place = pygame.Rect((0, 0), SPRITE_SIZES[sprite_name])
    place.center = box.center
    return place
