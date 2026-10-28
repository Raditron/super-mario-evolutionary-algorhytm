"""The window, the renderers and the keyboard (#8)."""

WINDOW_TITLE = "Mario World 1-1"
WINDOW_SCALE = 3
FRAMES_PER_SECOND = 60

# --- Keyboard (play mode). Names as pygame.key.key_code() reads them. ----------------

KEYBOARD_BUTTON_KEYS = {
    "left": "left",
    "right": "right",
    "down": "down",
    "jump": "x",
    "run": "z",
}
QUIT_KEY = "escape"
VIEW_TOGGLE_KEY = "f1"                    # switches between the Sprite view and the Debug view

# --- Debug view colours (RGB) ------------------------------------------------------------

SKY_COLOUR = (92, 148, 252)
GROUND_COLOUR = (200, 76, 12)
HARD_BLOCK_COLOUR = (136, 20, 0)
BRICK_COLOUR = (228, 92, 16)
QUESTION_BLOCK_COLOUR = (252, 188, 60)
USED_BLOCK_COLOUR = (160, 108, 40)
HIDDEN_BLOCK_COLOUR = (188, 188, 252)
PIPE_COLOUR = (0, 168, 0)
FLAGPOLE_COLOUR = (240, 240, 240)
CASTLE_STOPPER_COLOUR = (60, 60, 60)
MARIO_COLOUR = (216, 40, 0)                  # small or big
FIRE_MARIO_COLOUR = (252, 252, 252)
GOOMBA_COLOUR = (136, 76, 0)
# A defeated enemy (so far only a squashed Goomba) is drawn flattened to this
# height, standing on its feet.
DEFEATED_ENEMY_DRAWN_HEIGHT_PIXELS = 8
SUPER_MUSHROOM_COLOUR = (252, 116, 180)
ONE_UP_MUSHROOM_COLOUR = (0, 200, 120)
FIRE_FLOWER_COLOUR = (252, 160, 68)
FIREBALL_COLOUR = (252, 216, 0)
EXPLODING_FIREBALL_COLOUR = (252, 100, 0)
# While he can't be hurt, Mario is drawn only on ticks that are a multiple of this
# (PlayerGfxHandler skips him on odd frames while InjuryTimer runs).
INVULNERABLE_MARIO_DRAWN_EVERY_TICKS = 2

# --- Debug view: the followed agent's Observation and recent game events (#25) ---------------

# The Observation's 13 x 12 window is drawn over the level, each cell tinted by
# its value (RGB), at this opacity (0 transparent to 255 opaque), with this gap
# between cells so each one shows.
OBSERVATION_EMPTY_TINT = (0, 0, 0)
OBSERVATION_SOLID_TINT = (255, 255, 255)
OBSERVATION_ENEMY_TINT = (255, 0, 64)
OBSERVATION_TINT_OPACITY = 96
OBSERVATION_CELL_GAP_PIXELS = 1
# The four state numbers, as one line of text: a label for each, in the Observation's order.
OBSERVATION_STATE_LABELS = ("vx", "vy", "height", "ground")
OBSERVATION_STATE_DECIMALS = 2
OBSERVATION_STATE_TEXT_TOP_LEFT = (8, 228)
# Of the snapshot's recent game events, the newest few are listed.
DEBUG_GAME_EVENT_LINES = 4
DEBUG_GAME_EVENTS_TOP_LEFT = (8, 36)
DEBUG_TEXT_LINE_PIXELS = 9
DEBUG_TEXT_COLOUR = (252, 252, 252)
DEBUG_TEXT_BACKGROUND_COLOUR = (0, 0, 0)
DEBUG_FONT_SIZE = 14                      # pygame's default font, as the HUD uses

# --- HUD (TopStatusBarLine, StatusBarData, WriteBottomStatusLine) ----------------------------

# The original draws its status bar on the NES's 8 x 8 px text grid. Positions
# are (column, row) cells of that grid; each character fills one cell.
HUD_CELL_PIXELS = 8
HUD_TEXT_COLOUR = (252, 252, 252)
HUD_COIN_ICON_COLOUR = (252, 152, 56)
HUD_FONT_SIZE = 14                        # pygame's default font, unsmoothed: digits about 8 px tall
HUD_LABELS = {(3, 2): "MARIO", (18, 2): "WORLD", (25, 2): "TIME"}
# The score shows at least 6 digits, right-aligned in 7 cells: the original
# prints 7 and blanks the first while it is 0.
HUD_SCORE_CELL = (2, 3)
HUD_SCORE_CELLS_WIDE = 7
HUD_SCORE_MIN_DIGITS = 6
HUD_COIN_ICON_CELL = (11, 3)
HUD_COIN_ICON_RECT_IN_CELL = (2, 1, 4, 6)  # x, y, width, height in px
HUD_COIN_CROSS_CELL = (12, 3)
HUD_COIN_CROSS = "x"
HUD_COINS_CELL = (13, 3)
HUD_COINS_DIGITS = 2
HUD_WORLD_CELL = (19, 3)
HUD_TIME_CELL = (26, 3)
HUD_TIME_DIGITS = 3

# --- Sprite view (#32) -------------------------------------------------------------------------

# The sprites folder, from the repo root, and the one file type read from it.
# assets/sprites/README.md lists the file names and sizes.
SPRITES_FOLDER_PARTS = ("assets", "sprites")
SPRITE_FILE_EXTENSION = ".png"
# The original's sizes (width, height) in px. Tiles and scenery are one 16 x 16
# metatile each. The player object is 16 x 32, small Mario its lower 16 rows; an
# enemy object is 16 x 24 with the Goomba in its lower 16 rows and the defeated
# Goomba in its lowest 8 (EnemyGraphicsTable); a power-up is two rows of two
# 8 x 8 tiles, 16 x 16 (PowerUpGfxTable, DrawPowerUp); a fireball is one 8 x 8
# sprite and its explosion four, 16 x 16 (DrawExplosion_Fireball).
TILE_SPRITE_SIZE = (16, 16)
SMALL_MARIO_SPRITE_SIZE = (16, 16)
BIG_MARIO_SPRITE_SIZE = (16, 32)
GOOMBA_SPRITE_SIZE = (16, 16)
DEFEATED_GOOMBA_SPRITE_SIZE = (16, 8)
ITEM_SPRITE_SIZE = (16, 16)
FIREBALL_SPRITE_SIZE = (8, 8)
FIREBALL_EXPLOSION_SPRITE_SIZE = (16, 16)
# Every sprite the Sprite view draws: its file name (without the extension) and size.
SPRITE_SIZES = {
    # tiles, by how they look: the bricks and ? blocks don't show what they hold
    "ground": TILE_SPRITE_SIZE,
    "hard_block": TILE_SPRITE_SIZE,
    "brick": TILE_SPRITE_SIZE,
    "question_block": TILE_SPRITE_SIZE,
    "used_block": TILE_SPRITE_SIZE,
    "pipe": TILE_SPRITE_SIZE,
    "flagpole": TILE_SPRITE_SIZE,
    # background scenery
    "cloud": TILE_SPRITE_SIZE,
    "hill": TILE_SPRITE_SIZE,
    "bush": TILE_SPRITE_SIZE,
    "castle_battlement": TILE_SPRITE_SIZE,
    "castle_window": TILE_SPRITE_SIZE,
    "castle_brick": TILE_SPRITE_SIZE,
    "castle_door_arch": TILE_SPRITE_SIZE,
    "castle_door": TILE_SPRITE_SIZE,
    # Mario, by power state
    "mario_small": SMALL_MARIO_SPRITE_SIZE,
    "mario_big": BIG_MARIO_SPRITE_SIZE,
    "mario_fiery": BIG_MARIO_SPRITE_SIZE,
    # enemies
    "goomba": GOOMBA_SPRITE_SIZE,
    "goomba_defeated": DEFEATED_GOOMBA_SPRITE_SIZE,
    # items
    "super_mushroom": ITEM_SPRITE_SIZE,
    "one_up_mushroom": ITEM_SPRITE_SIZE,
    "fire_flower": ITEM_SPRITE_SIZE,
    # Mario's fireballs
    "fireball": FIREBALL_SPRITE_SIZE,
    "fireball_explosion": FIREBALL_EXPLOSION_SPRITE_SIZE,
}
# Scenery has no hitbox; a missing scenery sprite is drawn in these colours (RGB).
CLOUD_COLOUR = (252, 252, 252)
HILL_COLOUR = (0, 120, 0)
BUSH_COLOUR = (128, 208, 16)
CASTLE_BRICK_COLOUR = (172, 80, 36)
CASTLE_OPENING_COLOUR = (0, 0, 0)        # its windows and door
