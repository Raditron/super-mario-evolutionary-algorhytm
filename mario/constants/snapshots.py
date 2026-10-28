"""What a WorldSnapshot carries for the renderers (#25), and how watch-live hands them over (#29)."""

from mario.constants.physics import TICKS_PER_SECOND

# A snapshot holds the game events of the last this-many ticks (3 seconds at 60 fps).
RECENT_GAME_EVENT_TICKS = 180

# --- Watch-live (spec section 11) -----------------------------------------------------------

# Watched, a worker plays its chunk at the game's own speed, one tick per NES frame.
WATCHED_TICKS_PER_SECOND = TICKS_PER_SECOND
# Each chunk writes its snapshot into its own slot of shared memory, this big:
# room for a chunk of a few thousand agents.
SNAPSHOT_SLOT_BYTES = 1 << 20
# A slot starts with the length of the snapshot written into it, in this many bytes (0: none yet).
SNAPSHOT_LENGTH_BYTES = 8
