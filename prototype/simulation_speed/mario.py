"""Mario's momentum walk/run and held-jump physics (issue #2 constants). PROTOTYPE.

Simplified: no 10-frame run-cap hold, no big Mario, no ducking.
"""

from . import constants as c
from .tile_body import TileBody


class Mario(TileBody):
    __slots__ = ("jump_held_last_tick", "rising_gravity", "falling_gravity", "air_speed_cap")

    def __init__(self):
        super().__init__(c.MARIO_START_X_PIXELS, c.MARIO_START_ROW * c.TILE_SIZE_PIXELS,
                         c.MARIO_WIDTH_PIXELS, c.MARIO_HEIGHT_PIXELS)
        self.on_ground = True
        self.jump_held_last_tick = False
        self.rising_gravity = c.INITIAL_FALLING_GRAVITY
        self.falling_gravity = c.INITIAL_FALLING_GRAVITY
        self.air_speed_cap = c.MAX_WALK_SPEED

    def step(self, buttons: int, level) -> None:
        self._update_horizontal_speed(buttons)
        self._update_vertical_speed(buttons)
        if self.move_horizontally(level):
            self.velocity_x = 0
        self.move_vertically(level)

    def _update_horizontal_speed(self, buttons: int) -> None:
        holding_left = buttons & c.BUTTON_LEFT
        holding_right = buttons & c.BUTTON_RIGHT
        direction = 0
        if holding_right and not holding_left:
            direction = 1
        elif holding_left and not holding_right:
            direction = -1
        speed = abs(self.velocity_x)

        if self.on_ground:
            running = buttons & c.BUTTON_RUN
            speed_cap = c.MAX_RUN_SPEED if running else c.MAX_WALK_SPEED
            acceleration = c.RUN_ACCELERATION if running else c.WALK_ACCELERATION
            self.air_speed_cap = (c.MAX_RUN_SPEED if speed >= c.AIR_FAST_CAP_TAKEOFF_SPEED
                                  else c.MAX_WALK_SPEED)
        else:
            running = False
            speed_cap = self.air_speed_cap
            acceleration = c.WALK_ACCELERATION

        if direction == 0:
            if self.on_ground:
                self._apply_friction(speed)
            return                                    # no input in the air keeps speed

        if self.on_ground and self.velocity_x * direction < 0:
            if speed < c.SKID_TURNAROUND_SPEED:
                self.velocity_x = 0
            else:
                skid = c.SKID_DECELERATION_RUN if running else c.SKID_DECELERATION_WALK
                self.velocity_x += direction * skid
            return

        new_speed = self.velocity_x * direction + acceleration
        if new_speed > speed_cap:
            new_speed = max(speed_cap, speed - c.RELEASE_FRICTION)
        self.velocity_x = new_speed * direction

    def _apply_friction(self, speed: int) -> None:
        friction = (c.RELEASE_FRICTION_AFTER_RUN_SPEED if speed > c.MAX_WALK_SPEED
                    else c.RELEASE_FRICTION)
        new_speed = max(0, speed - friction)
        self.velocity_x = new_speed if self.velocity_x > 0 else -new_speed

    def _update_vertical_speed(self, buttons: int) -> None:
        jump_held = bool(buttons & c.BUTTON_JUMP)
        if jump_held and not self.jump_held_last_tick and self.on_ground:
            self._start_jump()
        self.jump_held_last_tick = jump_held

        gravity = self.rising_gravity if (self.velocity_y < 0 and jump_held) else self.falling_gravity
        self.velocity_y = min(self.velocity_y + gravity, c.TERMINAL_FALL_SPEED)

    def _start_jump(self) -> None:
        takeoff_speed = abs(self.velocity_x)
        if takeoff_speed < c.SLOW_JUMP_TAKEOFF_SPEED_LIMIT:
            self.velocity_y = c.SLOW_JUMP_VELOCITY
            self.rising_gravity = c.SLOW_JUMP_GRAVITY_HELD
            self.falling_gravity = c.SLOW_JUMP_GRAVITY_FALLING
        elif takeoff_speed < c.MEDIUM_JUMP_TAKEOFF_SPEED_LIMIT:
            self.velocity_y = c.SLOW_JUMP_VELOCITY
            self.rising_gravity = c.MEDIUM_JUMP_GRAVITY_HELD
            self.falling_gravity = c.MEDIUM_JUMP_GRAVITY_FALLING
        else:
            self.velocity_y = c.FAST_JUMP_VELOCITY
            self.rising_gravity = c.FAST_JUMP_GRAVITY_HELD
            self.falling_gravity = c.FAST_JUMP_GRAVITY_FALLING
        self.on_ground = False

    def bounce_off_stomp(self) -> None:
        self.velocity_y = c.STOMP_BOUNCE_VELOCITY

    def state(self) -> tuple:
        return (self.x, self.y, self.velocity_x, self.velocity_y, self.on_ground,
                self.jump_held_last_tick, self.rising_gravity, self.falling_gravity,
                self.air_speed_cap)
