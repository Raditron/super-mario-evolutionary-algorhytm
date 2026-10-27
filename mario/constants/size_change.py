"""Mario growing and shrinking (#19), and catching fire (#20): how long the game
stands still, when his size flips and the animation his body follows (SetPRout,
PlayerChangeSize, PlayerInjuryBlink, PlayerFireFlower, HandleChangeSize)."""

# While Mario changes size, the whole game stands still: TimerControl is set to
# $FF and counts down one a tick, and play resumes once it reaches $C4 (growing)
# or $C8 (shrinking). Timers, enemies and items wait too.
SIZE_CHANGE_TIMER_START = 0xFF
GROW_TICKS = SIZE_CHANGE_TIMER_START - 0xC4
SHRINK_TICKS = SIZE_CHANGE_TIMER_START - 0xC8
# Catching fire (UpToFiery) freezes the game the same way, until $C0
# (PlayerFireFlower); his size doesn't change.
CATCH_FIRE_TICKS = SIZE_CHANGE_TIMER_START - 0xC0
# His size flips once it reaches $F8 (growing) or $F0 (shrinking).
GROW_SIZE_FLIP_TICK = SIZE_CHANGE_TIMER_START - 0xF8
SHRINK_SIZE_FLIP_TICK = SIZE_CHANGE_TIMER_START - 0xF0

# From his size flip on, his body follows the original's animation, each frame
# for 4 ticks (HandleChangeSize steps every fourth frame, FrameCounter & 3).
# Frames are 0 small, 1 the intermediate grow frame and 2 big. Growing is
# ChangeSizeOffsetAdder's first ten entries; shrinking alternates the small and
# big swimming frames (its last ten: $02 small, $00 big). Before the flip he has
# his old body, after the animation his new one.
SIZE_CHANGE_FRAME_TICKS = 4
GROW_ANIMATION_FRAMES = (0, 1, 0, 1, 0, 1, 2, 0, 1, 2)
SHRINK_ANIMATION_FRAMES = (0, 2, 0, 2, 0, 2, 0, 2, 0, 2)
