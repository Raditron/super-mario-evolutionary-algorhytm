"""The Sprite view: the level as humans see it, every thing drawn with its sprite
from assets/sprites/ at the original's size, over the background scenery.

A watched generation's ghosts are their Mario sprites, translucent, under the
followed agent's. Mario, a ghost and a walking enemy face the way they face:
every sprite is drawn facing right, and mirrored for one facing left (a shell
looks the same either way, so it isn't). Mario, a ghost and a walking enemy
show the animation frame their snapshot names (#57); a frame whose sprite is
missing shows the standing sprite. A thing whose sprite is missing fills the
sprite's place in its hitbox colour, so the view works with an empty folder and
a PNG dropped in later shows with no code change (spec sections 8 and 12).

In the bonus room there is no scenery, and the background is black, as
underground. Mario and a ghost whom a pipe transition is moving are drawn behind
the tiles, as the original draws them (#23).
"""

import pygame

from mario.constants.animation import ENEMY_SECOND_WALK_FRAME
from mario.constants.level import TILE_SIZE_PIXELS
from mario.constants.view import (
    BUSH_COLOUR,
    CASTLE_BRICK_COLOUR,
    CASTLE_OPENING_COLOUR,
    CLOUD_COLOUR,
    EXPLODING_FIREBALL_COLOUR,
    FIREBALL_COLOUR,
    FLAG_COLOUR,
    GHOST_OPACITY,
    HILL_COLOUR,
    SPRITE_SIZES,
)
from mario.level.background_scenery import BackgroundScenery, SceneryKind
from mario.level.static_level import EnemyKind
from mario.level.tile_kind import TileKind
from mario.snapshots.world_snapshot import (
    AgentSnapshot,
    Area,
    EnemySnapshot,
    FireballSnapshot,
    FlagSnapshot,
    ItemKind,
    ItemSnapshot,
    MarioPose,
    MarioSnapshot,
    PowerState,
    VisibleTiles,
    WorldSnapshot,
    is_blinked_out,
)
from mario.view.area_backgrounds import AREA_BACKGROUND_COLOURS
from mario.view.hitbox_colours import ENEMY_COLOURS, ITEM_COLOURS, SHELL_COLOURS, TILE_COLOURS, mario_colour
from mario.view.pipe_sprite_names import (
    PipeNeighbourhood,
    SidePipeNeighbourhood,
    pipe_sprite_name,
    side_pipe_sprite_name,
)
from mario.view.scenery_sprite_names import SceneryNeighbourhood, scenery_sprite_name
from mario.view.sprite_library import SpriteLibrary

# Tiles by how they look: a brick or ? block doesn't show what it holds. A pipe
# tile, upright or sideways, is drawn by its place in its pipe (pipe_sprite_names). Other tiles not
# listed aren't drawn: open sky, the hidden 1-UP block until it is hit, and the
# castle stopper behind the castle.
TILE_SPRITE_NAMES = {
    TileKind.GROUND: "ground",
    TileKind.HARD_BLOCK: "hard_block",
    TileKind.BRICK: "brick",
    TileKind.STARMAN_BRICK: "brick",
    TileKind.MULTI_COIN_BRICK: "brick",
    TileKind.COIN_QUESTION_BLOCK: "question_block",
    TileKind.POWER_UP_QUESTION_BLOCK: "question_block",
    TileKind.USED_BLOCK: "used_block",
    TileKind.FLAGPOLE: "flagpole",
    TileKind.COIN: "coin_tile",
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

# Invincible, by size: the star palette shows over fire Mario's colours too.
INVINCIBLE_MARIO_SPRITE_NAMES = {
    PowerState.SMALL: "mario_small_invincible",
    PowerState.BIG: "mario_big_invincible",
    PowerState.FIERY: "mario_big_invincible",
}

# Mario's animation frames: his standing sprite's name, then the pose's ending;
# a walking frame's ending is numbered 1 to 3. Standing, he shows the standing sprite.
MARIO_POSE_SPRITE_SUFFIXES = {
    MarioPose.SKIDDING: "_skid",
    MarioPose.JUMPING: "_jump",
    MarioPose.CROUCHING: "_crouch",
}
WALK_FRAME_SPRITE_SUFFIX = "_walk_{}"

ENEMY_SPRITE_NAMES = {
    EnemyKind.GOOMBA: "goomba",
    EnemyKind.KOOPA: "koopa",
}

# A walking enemy's second walking frame; its first is its own sprite.
ENEMY_SECOND_WALK_FRAME_SPRITE_NAMES = {
    EnemyKind.GOOMBA: "goomba_walk_2",
    EnemyKind.KOOPA: "koopa_walk_2",
}

DEFEATED_ENEMY_SPRITE_NAMES = {
    EnemyKind.GOOMBA: "goomba_defeated",
}

SHELL_SPRITE_NAMES = {
    EnemyKind.KOOPA: "koopa_shell",
}

ITEM_SPRITE_NAMES = {
    ItemKind.SUPER_MUSHROOM: "super_mushroom",
    ItemKind.ONE_UP_MUSHROOM: "one_up_mushroom",
    ItemKind.FIRE_FLOWER: "fire_flower",
    ItemKind.STARMAN: "starman",
}

FIREBALL_SPRITE_NAME = "fireball"
FIREBALL_EXPLOSION_SPRITE_NAME = "fireball_explosion"
FLAG_SPRITE_NAME = "flag"


class SpriteRenderer:
    def __init__(self, sprites: SpriteLibrary, scenery: BackgroundScenery):
        self._sprites = sprites
        self._scenery = scenery

    def draw(self, snapshot: WorldSnapshot, screen: pygame.Surface) -> None:
        """Scenery behind the tiles, as in the original (the bonus room has none);
        items still rising out of their block behind them too, and Mario and the
        ghosts while a pipe transition moves them."""
        screen.fill(AREA_BACKGROUND_COLOURS[snapshot.area])
        if snapshot.area is Area.LEVEL:
            self._draw_scenery(snapshot, screen)
        for item in snapshot.items:
            if item.is_emerging:
                self._draw_item(item, snapshot.screen_left_x_pixels, screen)
        self._draw_agents(snapshot, screen, in_pipe=True)
        self._draw_tiles(snapshot, screen)
        if snapshot.flag is not None:
            self._draw_flag(snapshot.flag, snapshot.screen_left_x_pixels, screen)
        for item in snapshot.items:
            if not item.is_emerging:
                self._draw_item(item, snapshot.screen_left_x_pixels, screen)
        for enemy in snapshot.enemies:
            self._draw_enemy(enemy, snapshot.screen_left_x_pixels, screen)
        for fireball in snapshot.fireballs:
            self._draw_fireball(fireball, snapshot.screen_left_x_pixels, screen)
        self._draw_agents(snapshot, screen, in_pipe=False)

    def _draw_agents(self, snapshot: WorldSnapshot, screen: pygame.Surface, in_pipe: bool) -> None:
        """The ghosts, then Mario over them: those a pipe transition is moving, or the others."""
        for ghost in snapshot.ghosts:
            if ghost.mario.is_in_pipe is in_pipe:
                self._draw_ghost(ghost, snapshot.screen_left_x_pixels, screen)
        mario = snapshot.mario
        if mario.is_in_pipe is in_pipe and not is_blinked_out(mario.is_invulnerable, snapshot.tick):
            self._draw_mario(mario, snapshot.screen_left_x_pixels, screen)

    def _draw_scenery(self, snapshot: WorldSnapshot, screen: pygame.Surface) -> None:
        """Behind every tile the screen shows, each with the picture its scenery neighbours pick."""
        tiles = snapshot.tiles
        for row, kinds in enumerate(tiles.rows):
            for column in range(tiles.first_column, tiles.first_column + len(kinds)):
                neighbourhood = SceneryNeighbourhood.around(self._scenery, column, row)
                if neighbourhood is not None:
                    sprite_name = scenery_sprite_name(neighbourhood)
                    self._draw_sprite(sprite_name, SCENERY_COLOURS[neighbourhood.kind],
                                      _standing_on(_tile_box(column, row), sprite_name),
                                      snapshot.screen_left_x_pixels, screen)

    def _draw_tiles(self, snapshot: WorldSnapshot, screen: pygame.Surface) -> None:
        """Every tile in its place, a bouncing block raised above it."""
        tiles = snapshot.tiles
        bounce_offsets = {(block.column, block.row): block.offset_y_pixels for block in snapshot.bouncing_blocks}
        for row, kinds in enumerate(tiles.rows):
            for column_offset, kind in enumerate(kinds):
                column = tiles.first_column + column_offset
                sprite_name = _tile_sprite_name(tiles, kind, column, row)
                if sprite_name is None:
                    continue
                tile_box = _tile_box(column, row).move(0, bounce_offsets.get((column, row), 0))
                self._draw_sprite(sprite_name, TILE_COLOURS[kind], _standing_on(tile_box, sprite_name),
                                  snapshot.screen_left_x_pixels, screen)

    def _draw_mario(self, mario: MarioSnapshot, screen_left_x_pixels: int, screen: pygame.Surface) -> None:
        sprite_name = self._frame_or_standing(_mario_frame_sprite_name(mario), _mario_sprite_name(mario))
        self._draw_sprite(sprite_name, mario_colour(mario), _standing_on(_hitbox(mario), sprite_name),
                          screen_left_x_pixels, screen, is_mirrored=not mario.faces_right)

    def _draw_ghost(self, ghost: AgentSnapshot, screen_left_x_pixels: int, screen: pygame.Surface) -> None:
        """His Mario's sprite (or its place, filled), drawn at GHOST_OPACITY."""
        mario = ghost.mario
        sprite_name = self._frame_or_standing(_mario_frame_sprite_name(mario), _mario_sprite_name(mario))
        place = _standing_on(_hitbox(mario), sprite_name)
        ghost_surface = pygame.Surface(place.size, pygame.SRCALPHA)
        self._draw_sprite(sprite_name, mario_colour(mario), place.move(-place.x, -place.y), 0, ghost_surface,
                          is_mirrored=not ghost.faces_right)
        ghost_surface.set_alpha(GHOST_OPACITY)
        screen.blit(ghost_surface, place.move(-screen_left_x_pixels, 0))

    def _draw_enemy(self, enemy: EnemySnapshot, screen_left_x_pixels: int, screen: pygame.Surface) -> None:
        """A shell, even a defeated one (the original flips it), is drawn as its shell,
        never mirrored: the original draws it symmetric (MirrorEnemyGfx). A walking
        enemy shows its walking frame."""
        if enemy.is_shell:
            sprite_name, colour = SHELL_SPRITE_NAMES[enemy.kind], SHELL_COLOURS[enemy.kind]
        elif enemy.is_defeated:
            sprite_name, colour = DEFEATED_ENEMY_SPRITE_NAMES[enemy.kind], ENEMY_COLOURS[enemy.kind]
        else:
            sprite_name, colour = ENEMY_SPRITE_NAMES[enemy.kind], ENEMY_COLOURS[enemy.kind]
            if enemy.walk_frame == ENEMY_SECOND_WALK_FRAME:
                sprite_name = self._frame_or_standing(ENEMY_SECOND_WALK_FRAME_SPRITE_NAMES[enemy.kind], sprite_name)
        self._draw_sprite(sprite_name, colour, _standing_on(_hitbox(enemy), sprite_name), screen_left_x_pixels, screen,
                          is_mirrored=not enemy.is_shell and not enemy.faces_right)

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

    def _draw_flag(self, flag: FlagSnapshot, screen_left_x_pixels: int, screen: pygame.Surface) -> None:
        """From its top-left corner, on the left of the pole (FlagpoleGfxHandler)."""
        place = pygame.Rect((flag.x_pixels, flag.y_pixels), SPRITE_SIZES[FLAG_SPRITE_NAME])
        self._draw_sprite(FLAG_SPRITE_NAME, FLAG_COLOUR, place, screen_left_x_pixels, screen)

    def _frame_or_standing(self, frame_sprite_name: str, standing_sprite_name: str) -> str:
        """The frame's sprite while its picture is there; otherwise the standing sprite,
        whose place is filled in the colour while its picture is missing too."""
        return frame_sprite_name if self._sprites.sprite(frame_sprite_name) is not None else standing_sprite_name

    def _draw_sprite(self, sprite_name: str, hitbox_colour: tuple[int, int, int], place: pygame.Rect,
                     screen_left_x_pixels: int, screen: pygame.Surface, is_mirrored: bool = False) -> None:
        """The sprite in its place, given in level pixels, mirrored left to right in that same
        place for a thing facing left (DrawSpriteObject); while it is missing, its place in the colour."""
        place_on_screen = place.move(-screen_left_x_pixels, 0)
        sprite = self._sprites.sprite(sprite_name)
        if sprite is None:
            screen.fill(hitbox_colour, place_on_screen)
        elif is_mirrored:
            screen.blit(pygame.transform.flip(sprite, True, False), place_on_screen)
        else:
            screen.blit(sprite, place_on_screen)


def _tile_sprite_name(tiles: VisibleTiles, kind: TileKind, column: int, row: int) -> str | None:
    """The tile's sprite name, a pipe tile's picked by its place in its pipe; None for a tile not drawn."""
    if kind is TileKind.PIPE:
        return pipe_sprite_name(PipeNeighbourhood.around(tiles, column, row))
    if kind is TileKind.SIDE_PIPE:
        return side_pipe_sprite_name(SidePipeNeighbourhood.around(tiles, column, row))
    return TILE_SPRITE_NAMES.get(kind)


def _mario_sprite_name(mario: MarioSnapshot) -> str:
    """His standing sprite's name."""
    sprite_names = INVINCIBLE_MARIO_SPRITE_NAMES if mario.is_invincible else MARIO_SPRITE_NAMES
    return sprite_names[mario.power_state]


def _mario_frame_sprite_name(mario: MarioSnapshot) -> str:
    """The sprite of the animation frame he shows: his standing sprite's, with his pose's ending."""
    standing_sprite_name = _mario_sprite_name(mario)
    if mario.pose is MarioPose.STANDING:
        return standing_sprite_name
    if mario.pose is MarioPose.WALKING:
        return standing_sprite_name + WALK_FRAME_SPRITE_SUFFIX.format(mario.walk_frame)
    return standing_sprite_name + MARIO_POSE_SPRITE_SUFFIXES[mario.pose]


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
