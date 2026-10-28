"""Each kind of thing's hitbox colour. The Debug view fills hitboxes with them,
and the Sprite view fills a thing's place with them while its sprite is missing."""

from mario.constants.view import (
    BRICK_COLOUR,
    CASTLE_STOPPER_COLOUR,
    FIRE_FLOWER_COLOUR,
    FIRE_MARIO_COLOUR,
    FLAGPOLE_COLOUR,
    GOOMBA_COLOUR,
    GROUND_COLOUR,
    HARD_BLOCK_COLOUR,
    HIDDEN_BLOCK_COLOUR,
    MARIO_COLOUR,
    ONE_UP_MUSHROOM_COLOUR,
    PIPE_COLOUR,
    QUESTION_BLOCK_COLOUR,
    SUPER_MUSHROOM_COLOUR,
    USED_BLOCK_COLOUR,
)
from mario.level.static_level import EnemyKind
from mario.level.tile_kind import TileKind
from mario.snapshots.world_snapshot import ItemKind, PowerState

TILE_COLOURS = {
    TileKind.GROUND: GROUND_COLOUR,
    TileKind.HARD_BLOCK: HARD_BLOCK_COLOUR,
    TileKind.BRICK: BRICK_COLOUR,
    TileKind.COIN_QUESTION_BLOCK: QUESTION_BLOCK_COLOUR,
    TileKind.POWER_UP_QUESTION_BLOCK: QUESTION_BLOCK_COLOUR,
    TileKind.STARMAN_BRICK: BRICK_COLOUR,
    TileKind.MULTI_COIN_BRICK: BRICK_COLOUR,
    TileKind.HIDDEN_ONE_UP_BLOCK: HIDDEN_BLOCK_COLOUR,
    TileKind.USED_BLOCK: USED_BLOCK_COLOUR,
    TileKind.PIPE: PIPE_COLOUR,
    TileKind.FLAGPOLE: FLAGPOLE_COLOUR,
    TileKind.CASTLE_STOPPER: CASTLE_STOPPER_COLOUR,
}


ENEMY_COLOURS = {
    EnemyKind.GOOMBA: GOOMBA_COLOUR,
}


ITEM_COLOURS = {
    ItemKind.SUPER_MUSHROOM: SUPER_MUSHROOM_COLOUR,
    ItemKind.ONE_UP_MUSHROOM: ONE_UP_MUSHROOM_COLOUR,
    ItemKind.FIRE_FLOWER: FIRE_FLOWER_COLOUR,
}


MARIO_COLOURS = {
    PowerState.SMALL: MARIO_COLOUR,
    PowerState.BIG: MARIO_COLOUR,
    PowerState.FIERY: FIRE_MARIO_COLOUR,
}
