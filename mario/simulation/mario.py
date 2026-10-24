"""Mario's movement, as the original's PlayerCtrlRoutine runs it each frame (#2).

Speeds keep the original's split into a whole part, which moves Mario, and a
fraction, which only carries into the whole part. Every rule below names the
disassembly routine it comes from (docs/research/smb-physics-constants.md).
"""

from enum import Enum, auto

from mario.constants.level import (
    MARIO_START_SPRITE_X_PIXELS,
    MARIO_START_SPRITE_Y_PIXELS,
    PIT_DEATH_SPRITE_Y_PIXELS,
    SMALL_MARIO_HITBOX_HEIGHT_PIXELS,
    SMALL_MARIO_HITBOX_OFFSET_X_PIXELS,
    SMALL_MARIO_HITBOX_OFFSET_Y_PIXELS,
    SMALL_MARIO_HITBOX_WIDTH_PIXELS,
)
from mario.constants.physics import (
    AIR_RUN_CAP_SPEED,
    AREA_ENTRY_FALLING_GRAVITY,
    FAST_DECELERATION,
    FAST_DECELERATION_SPEED,
    FAST_JUMP_FALLING_GRAVITY,
    FAST_JUMP_RISING_GRAVITY,
    FAST_JUMP_SPEED,
    HEAD_BUMP_SPEED,
    JUMP_HALT_RISE_PIXELS,
    MARIO_TERMINAL_FALL_SPEED,
    MEDIUM_JUMP_FALLING_GRAVITY,
    MEDIUM_JUMP_RISING_GRAVITY,
    MEDIUM_JUMP_SPEED,
    MEDIUM_JUMP_SPEED_LIMIT,
    RUN_ACCELERATION,
    RUN_SPEED_CAP,
    RUNNING_SPEED_FLAG_SPEED,
    RUNNING_TIMER_TICKS,
    SKID_ACCELERATION_MULTIPLIER,
    SKID_TURNAROUND_SPEED,
    SLOW_JUMP_FALLING_GRAVITY,
    SLOW_JUMP_RISING_GRAVITY,
    SLOW_JUMP_SPEED,
    SLOW_JUMP_SPEED_LIMIT,
    STOMP_BOUNCE_SPEED,
    SUBPIXEL_BITS,
    SUBPIXEL_FRACTION_MASK,
    SUBPIXELS_PER_PIXEL,
    WALK_ACCELERATION,
    WALK_SPEED_CAP,
    X_SUBSPEED_MASK,
    Y_SUBSPEED_MASK,
)
from mario.controller.controller_state import LEFT, NO_DIRECTION, RIGHT, ControllerState
from mario.level.static_level import StaticLevel
from mario.simulation.gravity import add_gravity
from mario.simulation.tile_body import TileBody, VerticalContact


class MovementState(Enum):
    """The original's Player_State."""
    ON_GROUND = auto()
    JUMPING = auto()
    FALLING = auto()


class Mario(TileBody):
    """Small Mario. His position is the top-left corner of his hitbox."""

    hitbox_offset_y_pixels = SMALL_MARIO_HITBOX_OFFSET_Y_PIXELS

    def __init__(self, screen_left_x_pixels: int = 0):
        """Mario starts at the original's start position on a screen whose left edge is given."""
        super().__init__(
            (screen_left_x_pixels + MARIO_START_SPRITE_X_PIXELS + SMALL_MARIO_HITBOX_OFFSET_X_PIXELS)
            * SUBPIXELS_PER_PIXEL,
            (MARIO_START_SPRITE_Y_PIXELS + SMALL_MARIO_HITBOX_OFFSET_Y_PIXELS) * SUBPIXELS_PER_PIXEL,
            SMALL_MARIO_HITBOX_WIDTH_PIXELS * SUBPIXELS_PER_PIXEL,
            SMALL_MARIO_HITBOX_HEIGHT_PIXELS * SUBPIXELS_PER_PIXEL,
        )
        self.velocity_x = 0
        self.velocity_y = 0
        self.movement_state = MovementState.ON_GROUND
        self.facing_direction = RIGHT
        self.moving_direction = RIGHT
        # |whole x speed| as of the last friction step (Player_XSpeedAbsolute)
        self.x_speed_absolute = 0
        self.running_timer = 0
        self.running_speed_flag = False
        self.speed_cap = WALK_SPEED_CAP
        self.acceleration = WALK_ACCELERATION
        self.gravity = AREA_ENTRY_FALLING_GRAVITY
        self.falling_gravity = AREA_ENTRY_FALLING_GRAVITY
        self.jump_origin_y_pixels = 0
        self.jump_held_last_tick = False
        # the left/right the movement used, after crouch-stopping (Left_Right_Buttons)
        self.held_direction = NO_DIRECTION

    @property
    def pixel_x(self) -> int:
        return self.x >> SUBPIXEL_BITS

    @property
    def pixel_y(self) -> int:
        return self.y >> SUBPIXEL_BITS

    @property
    def has_fallen_in_pit(self) -> bool:
        """True once he has fallen below the screen."""
        return self.sprite_top_has_reached(PIT_DEATH_SPRITE_Y_PIXELS)

    @property
    def is_on_ground(self) -> bool:
        return self.movement_state is MovementState.ON_GROUND

    def step(self, controller: ControllerState, level: StaticLevel) -> None:
        if self.running_timer > 0:
            self.running_timer -= 1
        self.held_direction = controller.direction
        if controller.down and self.is_on_ground:
            self.held_direction = NO_DIRECTION
        self._start_jump_on_fresh_press(controller)
        self._choose_horizontal_physics(controller)
        if self.is_on_ground:
            self._update_running_speed_and_skid(controller)
            if self.held_direction != NO_DIRECTION:
                self.facing_direction = self.held_direction
            self._impose_friction()
            self._move_horizontally(level)
        else:
            self._choose_gravity(controller)
            if self.held_direction != NO_DIRECTION:
                self._impose_friction()
            self._move_horizontally(level)
            self._move_vertically(level)
        whole_speed_x = self._whole_speed_x()
        if whole_speed_x != 0:
            self.moving_direction = RIGHT if whole_speed_x > 0 else LEFT
        if self.is_on_ground and not self.is_standing_on_solid_tile(level):
            self.movement_state = MovementState.FALLING
        self.jump_held_last_tick = controller.jump

    def stop_at_screen_edge(self, pixel_x: int, keeps_speed: bool) -> None:
        """Hold Mario at a screen edge (the original's KeepOnscr)."""
        self.x = pixel_x * SUBPIXELS_PER_PIXEL + (self.x & SUBPIXEL_FRACTION_MASK)
        if not keeps_speed:
            self.velocity_x &= X_SUBSPEED_MASK

    def bounce_off_enemy(self) -> None:
        """After a stomp (EnemyStomped): rise again at the bounce speed. The speed's
        fraction and the gravity are kept."""
        self.velocity_y = STOMP_BOUNCE_SPEED + (self.velocity_y & Y_SUBSPEED_MASK)

    # --- PlayerPhysicsSub ---------------------------------------------------------------

    def _start_jump_on_fresh_press(self, controller: ControllerState) -> None:
        """ProcJumping: the takeoff speed picks the jump's speed and gravities."""
        if not controller.jump or self.jump_held_last_tick or not self.is_on_ground:
            return
        if self.x_speed_absolute < SLOW_JUMP_SPEED_LIMIT:
            jump_speed, self.gravity, self.falling_gravity = (
                SLOW_JUMP_SPEED, SLOW_JUMP_RISING_GRAVITY, SLOW_JUMP_FALLING_GRAVITY)
        elif self.x_speed_absolute < MEDIUM_JUMP_SPEED_LIMIT:
            jump_speed, self.gravity, self.falling_gravity = (
                MEDIUM_JUMP_SPEED, MEDIUM_JUMP_RISING_GRAVITY, MEDIUM_JUMP_FALLING_GRAVITY)
        else:
            jump_speed, self.gravity, self.falling_gravity = (
                FAST_JUMP_SPEED, FAST_JUMP_RISING_GRAVITY, FAST_JUMP_FALLING_GRAVITY)
        self.velocity_y = jump_speed
        self.y -= self.y & SUBPIXEL_FRACTION_MASK
        self.jump_origin_y_pixels = self.pixel_y
        self.movement_state = MovementState.JUMPING

    def _choose_horizontal_physics(self, controller: ControllerState) -> None:
        """X_Physics: the speed cap and acceleration for this tick."""
        if self.is_on_ground:
            holding_moving_direction = self.held_direction == self.moving_direction
            if holding_moving_direction and controller.run:
                self.running_timer = RUNNING_TIMER_TICKS
            runs = holding_moving_direction and (controller.run or self.running_timer > 0)
        else:
            runs = self.x_speed_absolute >= AIR_RUN_CAP_SPEED
        if runs:
            self.speed_cap = RUN_SPEED_CAP
            self.acceleration = RUN_ACCELERATION
        else:
            self.speed_cap = WALK_SPEED_CAP
            fast = self.running_speed_flag or self.x_speed_absolute >= FAST_DECELERATION_SPEED
            self.acceleration = FAST_DECELERATION if fast else WALK_ACCELERATION
        if self.facing_direction != self.moving_direction:
            self.acceleration *= SKID_ACCELERATION_MULTIPLIER

    # --- OnGroundStateSub / JumpSwimSub / FallingSub -----------------------------------------

    def _update_running_speed_and_skid(self, controller: ControllerState) -> None:
        """GetPlayerAnimSpeed: the RunningSpeed flag, and the turnaround at the end of a skid."""
        if self.x_speed_absolute >= RUNNING_SPEED_FLAG_SPEED:
            self.running_speed_flag = True
        elif controller.holds_any_button_but_jump:
            if controller.direction == self.moving_direction:
                self.running_speed_flag = False
            elif self.x_speed_absolute < SKID_TURNAROUND_SPEED:
                self.moving_direction = self.facing_direction
                self.velocity_x = 0

    def _impose_friction(self) -> None:
        """ImposeFriction: accelerate toward the held direction, or slow down without one."""
        if self.held_direction == RIGHT:
            self._speed_up_rightwards()
        elif self.held_direction == LEFT:
            self._speed_up_leftwards()
        elif self._whole_speed_x() > 0:
            self._speed_up_leftwards()
        elif self._whole_speed_x() < 0:
            self._speed_up_rightwards()
        self.x_speed_absolute = abs(self._whole_speed_x())

    def _speed_up_rightwards(self) -> None:
        self.velocity_x += self.acceleration
        if self._whole_speed_x() >= self.speed_cap:
            self.velocity_x = self.speed_cap + (self.velocity_x & X_SUBSPEED_MASK)

    def _speed_up_leftwards(self) -> None:
        self.velocity_x -= self.acceleration
        if self._whole_speed_x() < -self.speed_cap:
            self.velocity_x = -self.speed_cap + (self.velocity_x & X_SUBSPEED_MASK)

    def _choose_gravity(self, controller: ControllerState) -> None:
        """JumpSwimSub / FallingSub: rising gravity only while rising with jump held."""
        if self.movement_state is MovementState.FALLING or self.velocity_y >= 0:
            self.gravity = self.falling_gravity
            return
        if controller.jump and self.jump_held_last_tick:
            return
        if self.jump_origin_y_pixels - self.pixel_y < JUMP_HALT_RISE_PIXELS:
            return
        self.gravity = self.falling_gravity

    def _move_horizontally(self, level: StaticLevel) -> None:
        if self.move_horizontally(level, self._whole_speed_x()):
            self.velocity_x &= X_SUBSPEED_MASK

    def _move_vertically(self, level: StaticLevel) -> None:
        """ImposeGravity, then the original's landing and head-bump responses."""
        contact = self.move_vertically(level, self.velocity_y)
        self.velocity_y = add_gravity(self.velocity_y, self.gravity, MARIO_TERMINAL_FALL_SPEED)
        if contact is VerticalContact.LANDED:
            self.velocity_y = 0
            self.movement_state = MovementState.ON_GROUND
        elif contact is VerticalContact.HIT_CEILING:
            self.velocity_y = HEAD_BUMP_SPEED + (self.velocity_y & Y_SUBSPEED_MASK)

    def _whole_speed_x(self) -> int:
        return self.velocity_x - (self.velocity_x & X_SUBSPEED_MASK)
