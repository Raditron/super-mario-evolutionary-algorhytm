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

# --- Debug view colours (RGB) ------------------------------------------------------------

SKY_COLOUR = (92, 148, 252)
GROUND_COLOUR = (200, 76, 12)
HARD_BLOCK_COLOUR = (136, 20, 0)
BRICK_COLOUR = (228, 92, 16)
QUESTION_BLOCK_COLOUR = (252, 188, 60)
HIDDEN_BLOCK_COLOUR = (188, 188, 252)
PIPE_COLOUR = (0, 168, 0)
FLAGPOLE_COLOUR = (240, 240, 240)
CASTLE_STOPPER_COLOUR = (60, 60, 60)
MARIO_COLOUR = (216, 40, 0)
