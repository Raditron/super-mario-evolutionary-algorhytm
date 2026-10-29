"""The keys every drawing may use, whatever its group."""

Colour = tuple[int, int, int, int]  # RGBA

TRANSPARENT = (0, 0, 0, 0)
OUTLINE = (16, 16, 24, 255)
WHITE = (252, 252, 252, 255)

SHARED_KEYS = {
    ".": TRANSPARENT,
    "K": OUTLINE,
    "W": WHITE,
}
