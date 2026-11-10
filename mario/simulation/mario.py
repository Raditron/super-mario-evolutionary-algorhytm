"""Mario's movement, as the original's PlayerCtrlRoutine runs it each frame (#2).

Speeds keep the original's split into a whole part, which moves Mario, and a
fraction, which only carries into the whole part. Every rule below names the
disassembly routine it comes from (docs/research/smb-physics-constants.md).

Big (and fire) Mario moves exactly as small Mario does; only his box differs:
taller, or small Mario's while he crouches. Changing his power state (growing,
shrinking or catching fire: PowerStateChange) stops him and the whole game for
a while; after shrinking he can't be hurt for a while. A Starman makes him
invincible for a while. Growing or standing up can put his box inside a solid
tile, which his head and side probes then get him out of, as in the original.

Once a tick, after everything has moved, he picks the animation frame he shows
(animate, MarioAnimation).
"""

from enum import Enum, auto

from mario.constants.level import (
    BIG_MARIO_HITBOX_HEIGHT_PIXELS,
    BIG_MARIO_HITBOX_OFFSET_Y_PIXELS,
    BIG_MARIO_SIDE_PROBE_SPRITE_Y_PIXELS,
    HEAD_PROBE_MIN_DEPTH_PIXELS,
    INTERMEDIATE_MARIO_HITBOX_HEIGHT_PIXELS,
    INTERMEDIATE_MARIO_HITBOX_OFFSET_Y_PIXELS,
    MARIO_START_SPRITE_X_PIXELS,
    MARIO_START_SPRITE_Y_PIXELS,
    PIT_DEATH_SPRITE_Y_PIXELS,
    SMALL_MARIO_HITBOX_HEIGHT_PIXELS,
    SMALL_MARIO_HITBOX_OFFSET_X_PIXELS,
    SMALL_MARIO_HITBOX_OFFSET_Y_PIXELS,
    SMALL_MARIO_HITBOX_WIDTH_PIXELS,
    SMALL_MARIO_SIDE_PROBE_SPRITE_Y_PIXELS,
    SUBPIXEL_TO_TILE_SHIFT,
    TILE_SIZE_PIXELS,
)
from mario.constants.animation import SKID_FRAME_MIN_SPEED
from mario.constants.physics import (
    AIR_RUN_CAP_SPEED,
    AREA_ENTRY_FALLING_GRAVITY,
    BLOCK_BUMP_SPEED,
    BRICK_BREAK_SPEED,
    FAST_DECELERATION,
    FAST_DECELERATION_SPEED,
    FAST_JUMP_FALLING_GRAVITY,
    FAST_JUMP_RISING_GRAVITY,
    FAST_JUMP_SPEED,
    HEAD_BUMP_SPEED,
    INJURY_INVULNERABLE_TICKS,
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
    SIDE_PUSH_PIXELS,
    SKID_TURNAROUND_SPEED,
    SLOW_JUMP_FALLING_GRAVITY,
    SLOW_JUMP_RISING_GRAVITY,
    SLOW_JUMP_SPEED,
    SLOW_JUMP_SPEED_LIMIT,
    STARMAN_INVINCIBLE_TICKS,
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
from mario.simulation.attempt_tiles import AttemptTiles
from mario.simulation.gravity import add_gravity
from mario.simulation.mario_animation import MarioAnimation, MarioPose, is_blinked_out
from mario.simulation.power_state_change import PowerState, PowerStateChange
from mario.simulation.size_change import MarioBody
from mario.simulation.tile_body import TileBody, VerticalContact


def count_down(ticks_left: int) -> int:
    """A timer one tick on, stopping at 0."""
    return ticks_left - 1 if ticks_left > 0 else ticks_left


class MovementState(Enum):
    """The original's Player_State."""
    ON_GROUND = auto()
    JUMPING = auto()
    FALLING = auto()


# Each body's box, as (how far below the sprite's top it starts, its height) in pixels.
BODY_BOXES_PIXELS = {
    MarioBody.SMALL: (SMALL_MARIO_HITBOX_OFFSET_Y_PIXELS, SMALL_MARIO_HITBOX_HEIGHT_PIXELS),
    MarioBody.INTERMEDIATE: (INTERMEDIATE_MARIO_HITBOX_OFFSET_Y_PIXELS, INTERMEDIATE_MARIO_HITBOX_HEIGHT_PIXELS),
    MarioBody.BIG: (BIG_MARIO_HITBOX_OFFSET_Y_PIXELS, BIG_MARIO_HITBOX_HEIGHT_PIXELS),
}
# The sprite y's of each body's side probes; nothing collides while the
# intermediate grow frame shows.
SIDE_PROBE_SPRITE_Y_PIXELS = {
    MarioBody.SMALL: SMALL_MARIO_SIDE_PROBE_SPRITE_Y_PIXELS,
    MarioBody.BIG: BIG_MARIO_SIDE_PROBE_SPRITE_Y_PIXELS,
}


class Mario(TileBody):
    """His position is the top-left corner of his hitbox."""

    def __init__(self, screen_left_x_pixels: int = 0):
        """Small Mario starts at the original's start position on a screen whose left edge is given."""
        self.hitbox_offset_y_pixels = SMALL_MARIO_HITBOX_OFFSET_Y_PIXELS
        super().__init__(
            (screen_left_x_pixels + MARIO_START_SPRITE_X_PIXELS + SMALL_MARIO_HITBOX_OFFSET_X_PIXELS)
            * SUBPIXELS_PER_PIXEL,
            (MARIO_START_SPRITE_Y_PIXELS + SMALL_MARIO_HITBOX_OFFSET_Y_PIXELS) * SUBPIXELS_PER_PIXEL,
            SMALL_MARIO_HITBOX_WIDTH_PIXELS * SUBPIXELS_PER_PIXEL,
            SMALL_MARIO_HITBOX_HEIGHT_PIXELS * SUBPIXELS_PER_PIXEL,
        )
        self.power_state = PowerState.SMALL
        self._body = MarioBody.SMALL
        self.is_dead = False                         # an enemy's touch killed him
        self._power_state_change: PowerStateChange | None = None
        self._start_afresh()

    def _start_afresh(self) -> None:
        """Everything about him but where he is and his power state, as an area
        starts: standing still, facing right, with no timer running."""
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
        self._jump_held_last_tick = False
        # the left/right the movement used, after crouch-stopping (Left_Right_Buttons)
        self.held_direction = NO_DIRECTION
        # (column, row) of the tile his head hit from below this tick: the one over
        # his centre, where the original's single head probe is (sprite x + 8)
        self.head_hit_tile: tuple[int, int] | None = None
        self._is_crouching = False                   # CrouchingFlag
        self._invulnerable_ticks_left = 0            # InjuryTimer
        self._invincible_ticks_left = 0              # StarInvincibleTimer
        self._run_held_last_tick = False
        # set each tick: fire Mario pressed run afresh while able to shoot (ProcFireball_Bubble)
        self.wants_to_shoot_fireball = False
        self.animation = MarioAnimation()

    @property
    def pixel_x(self) -> int:
        return self.x >> SUBPIXEL_BITS

    @property
    def pixel_y(self) -> int:
        return self.y >> SUBPIXEL_BITS

    @property
    def sprite_x_pixels(self) -> int:
        """The x of the original's 16 x 32 player sprite."""
        return self.pixel_x - SMALL_MARIO_HITBOX_OFFSET_X_PIXELS

    @property
    def sprite_y_pixels(self) -> int:
        """The y of the top of the original's 16 x 32 player sprite."""
        return self.pixel_y - self.hitbox_offset_y_pixels

    @property
    def whole_speed_x(self) -> int:
        """The part of his x speed that moves him (Player_X_Speed); the fraction only carries into it."""
        return self.velocity_x - (self.velocity_x & X_SUBSPEED_MASK)

    @property
    def has_fallen_in_pit(self) -> bool:
        """True once he has fallen below the screen."""
        return self.sprite_top_has_reached(PIT_DEATH_SPRITE_Y_PIXELS)

    @property
    def is_on_ground(self) -> bool:
        return self.movement_state is MovementState.ON_GROUND

    @property
    def is_big(self) -> bool:
        """Big or fiery: his body is big Mario's."""
        return self.power_state is not PowerState.SMALL

    @property
    def is_fiery(self) -> bool:
        return self.power_state is PowerState.FIERY

    @property
    def is_crouching(self) -> bool:
        """CrouchingFlag: big Mario holding down on the ground, and still so in the air."""
        return self._is_crouching

    @property
    def is_changing_power_state(self) -> bool:
        """While he grows, shrinks or catches fire, the whole game stands still."""
        return self._power_state_change is not None

    @property
    def is_invulnerable(self) -> bool:
        """Whether an enemy's touch can't hurt him: from being hurt until a while after he has shrunk."""
        return self._invulnerable_ticks_left > 0

    @property
    def is_invincible(self) -> bool:
        """Whether he is invincible, for a while after collecting a Starman: every
        enemy he touches is defeated, and none can hurt him."""
        return self._invincible_ticks_left > 0

    def step(self, controller: ControllerState, tiles: AttemptTiles) -> None:
        self.head_hit_tile = None
        self.running_timer = count_down(self.running_timer)
        self._invulnerable_ticks_left = count_down(self._invulnerable_ticks_left)
        self._invincible_ticks_left = count_down(self._invincible_ticks_left)
        self._update_crouching(controller)
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
            self._move_horizontally(tiles)
        else:
            self._choose_gravity(controller)
            if self.held_direction != NO_DIRECTION:
                self._impose_friction()
            self._move_horizontally(tiles)
            self._move_vertically(tiles)
        whole_speed_x = self.whole_speed_x
        if whole_speed_x != 0:
            self.moving_direction = RIGHT if whole_speed_x > 0 else LEFT
        self._get_out_of_solid_tiles(tiles)
        if self.is_on_ground and not self.is_standing_on_solid_tile(tiles):
            self.movement_state = MovementState.FALLING
        self._jump_held_last_tick = controller.jump
        self._check_for_fireball_shot(controller)

    def stop_at_screen_edge(self, pixel_x: int, keeps_speed: bool) -> None:
        """Hold Mario at a screen edge (the original's KeepOnscr)."""
        self.x = pixel_x * SUBPIXELS_PER_PIXEL + (self.x & SUBPIXEL_FRACTION_MASK)
        if not keeps_speed:
            self.velocity_x &= X_SUBSPEED_MASK

    def start_in_area(self, sprite_x_pixels: int, sprite_y_pixels: int) -> None:
        """A new area starts with his sprite here (InitializeArea). The original
        clears his memory but his power state (InitializeMemory), and its frame
        timers (ClrTimersLoop): he stands up, still, with neither a Starman's
        invincibility nor the while after being hurt."""
        self._take_body(MarioBody.BIG if self.is_big else MarioBody.SMALL)
        self.x = (sprite_x_pixels + SMALL_MARIO_HITBOX_OFFSET_X_PIXELS) * SUBPIXELS_PER_PIXEL
        self.y = (sprite_y_pixels + self.hitbox_offset_y_pixels) * SUBPIXELS_PER_PIXEL
        self._start_afresh()

    def move_through_tiles(self, distance_x: int, distance_y: int) -> None:
        """Move him by these sub-pixels whatever tiles are there, shooting nothing:
        in a pipe transition the original turns his tile collision off."""
        self.x += distance_x
        self.y += distance_y
        self.wants_to_shoot_fireball = False

    def hold_flagpole(self, sprite_x_pixels: int, sprite_y_pixels: int, facing_direction: int) -> None:
        """On the flagpole, his sprite here (PutPlayerOnVine), with no speed. Once
        let go of, he falls from there."""
        self.x = (sprite_x_pixels + SMALL_MARIO_HITBOX_OFFSET_X_PIXELS) * SUBPIXELS_PER_PIXEL
        self.y = (sprite_y_pixels + self.hitbox_offset_y_pixels) * SUBPIXELS_PER_PIXEL
        self.velocity_x = 0
        self.velocity_y = 0
        self.x_speed_absolute = 0
        self.facing_direction = facing_direction
        self.movement_state = MovementState.FALLING

    def bounce_off_enemy(self) -> None:
        """After a stomp (EnemyStomped): rise again at the bounce speed. The speed's
        fraction and the gravity are kept."""
        self.velocity_y = STOMP_BOUNCE_SPEED + (self.velocity_y & Y_SUBSPEED_MASK)

    def bump_block(self) -> None:
        """His head bumped the block it hit (BumpBlock): his rise stops dead. The
        speed's fraction is kept."""
        self.velocity_y = BLOCK_BUMP_SPEED + (self.velocity_y & Y_SUBSPEED_MASK)

    def break_brick(self) -> None:
        """His head broke the brick it hit (BrickShatter): he keeps rising, slower.
        The speed's fraction is kept."""
        self.velocity_y = BRICK_BREAK_SPEED + (self.velocity_y & Y_SUBSPEED_MASK)

    def power_up(self) -> None:
        """He collected a Super Mushroom or a fire flower (Shroom_Flower_PUp, which
        doesn't look at which): small, he grows; big, he catches fire; fiery,
        nothing changes."""
        if not self.is_big:
            self.grow()
        elif not self.is_fiery:
            self._catch_fire()

    def become_invincible(self) -> None:
        """He collected a Starman (HandlePowerUpCollision): invincible from now, for
        a while, whatever his power state, which it leaves alone."""
        self._invincible_ticks_left = STARMAN_INVINCIBLE_TICKS

    def grow(self) -> None:
        """Small, he collected a Super Mushroom or a fire flower. SetPRout puts him
        in the on-ground state wherever he is; he falls from there once play resumes."""
        self.movement_state = MovementState.ON_GROUND
        self._power_state_change = PowerStateChange.growing()

    def _catch_fire(self) -> None:
        """UpToFiery: fiery at once, and frozen for a while in the on-ground state,
        as for growing (SetPRout)."""
        self.power_state = PowerState.FIERY
        self.movement_state = MovementState.ON_GROUND
        self._power_state_change = PowerStateChange.catching_fire()

    def get_hurt(self) -> None:
        """An enemy hurt him (ForceInjury): small, he dies; big, he shrinks and
        can't be hurt for a while. Fiery, his fire goes at once (PlayerStatus,
        GetPlayerColors), his size only at the flip. SetKRout puts him in the
        jumping state."""
        if not self.is_big:
            self.is_dead = True
            return
        if self.is_fiery:
            self.power_state = PowerState.BIG
        self._is_crouching = False
        self.movement_state = MovementState.JUMPING
        self._power_state_change = PowerStateChange.shrinking()
        self._invulnerable_ticks_left = INJURY_INVULNERABLE_TICKS

    def continue_power_state_change(self, controller: ControllerState) -> None:
        """One tick of growing, shrinking or catching fire, in which nothing else
        moves and he shoots nothing. Where the change reads the Controller, the
        buttons are remembered, so a press must still be fresh when play resumes."""
        change = self._power_state_change
        change.step()
        if change.shown_body is not None:
            self._take_body(change.shown_body)
        if change.has_reached_power_state_after:
            self.power_state = change.power_state_after
        if change.is_over:
            self._power_state_change = None
        if change.reads_controller:
            self._jump_held_last_tick = controller.jump
            self._run_held_last_tick = controller.run
        self.wants_to_shoot_fireball = False
        self.animation.stand_through_power_state_change()

    def throw_fireball(self) -> None:
        """His fireball went into play this tick: his walking frame's time starts again."""
        self.animation.throw_fireball()

    def animate(self, tick: int) -> None:
        """PlayerGfxHandler, once a tick after everything has moved: the frame he
        shows. Falling off a ledge, he keeps the walking frame he had (ActionFalling).
        Blinking after being hurt, on a tick he isn't drawn, nothing is chosen."""
        if is_blinked_out(self.is_invulnerable, tick):
            self.animation.blink_out()
        elif self.movement_state is MovementState.FALLING:
            self.animation.keep_walk_frame()
        else:
            self.animation.show(self._pose())

    def _pose(self) -> MarioPose:
        """ProcessPlayerAction, jumping or on the ground: crouching if he crouches;
        in the air, jumping; on the ground, standing with no speed and no left or
        right held, skidding fast enough against the way he faces, else walking."""
        if self._is_crouching:
            return MarioPose.CROUCHING
        if self.movement_state is MovementState.JUMPING:
            return MarioPose.JUMPING
        if self.whole_speed_x == 0 and self.held_direction == NO_DIRECTION:
            return MarioPose.STANDING
        if self.x_speed_absolute >= SKID_FRAME_MIN_SPEED and self.moving_direction != self.facing_direction:
            return MarioPose.SKIDDING
        return MarioPose.WALKING

    def _check_for_fireball_shot(self, controller: ControllerState) -> None:
        """ProcFireball_Bubble, after he has moved: fiery, he shoots on a fresh run
        press, unless he is crouching or his sprite's top is above the screen
        (Player_Y_HighPos is not 1). Whether a fireball slot is free is for his
        fireballs to say."""
        run_pressed_afresh = controller.run and not self._run_held_last_tick
        self.wants_to_shoot_fireball = (self.is_fiery and run_pressed_afresh and not self._is_crouching
                                        and self.sprite_y_pixels >= 0)
        self._run_held_last_tick = controller.run

    def _update_crouching(self, controller: ControllerState) -> None:
        """PlayerMovementSubs: big Mario crouches while he holds down on the ground,
        and keeps it in the air. Crouching, his box is small Mario's."""
        if not self.is_big:
            self._is_crouching = False
        elif self.is_on_ground:
            self._is_crouching = controller.down
        body = MarioBody.BIG if self.is_big and not self._is_crouching else MarioBody.SMALL
        if body is not self._body:
            self._take_body(body)

    def _take_body(self, body: MarioBody) -> None:
        """Take that body's box, keeping his feet where they are."""
        self._body = body
        feet_y = self.feet_y
        self.hitbox_offset_y_pixels, height_pixels = BODY_BOXES_PIXELS[body]
        self.height = height_pixels * SUBPIXELS_PER_PIXEL
        self.y = feet_y - self.height

    # --- PlayerPhysicsSub ---------------------------------------------------------------

    def _start_jump_on_fresh_press(self, controller: ControllerState) -> None:
        """ProcJumping: the takeoff speed picks the jump's speed and gravities."""
        if not controller.jump or self._jump_held_last_tick or not self.is_on_ground:
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
        """GetPlayerAnimSpeed: how long each walking frame shows, the RunningSpeed
        flag, and the turnaround at the end of a skid."""
        self.animation.choose_walk_speed(self.x_speed_absolute)
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
        elif self.whole_speed_x > 0:
            self._speed_up_leftwards()
        elif self.whole_speed_x < 0:
            self._speed_up_rightwards()
        self.x_speed_absolute = abs(self.whole_speed_x)

    def _speed_up_rightwards(self) -> None:
        self.velocity_x += self.acceleration
        if self.whole_speed_x >= self.speed_cap:
            self.velocity_x = self.speed_cap + (self.velocity_x & X_SUBSPEED_MASK)

    def _speed_up_leftwards(self) -> None:
        self.velocity_x -= self.acceleration
        if self.whole_speed_x < -self.speed_cap:
            self.velocity_x = -self.speed_cap + (self.velocity_x & X_SUBSPEED_MASK)

    def _choose_gravity(self, controller: ControllerState) -> None:
        """JumpSwimSub / FallingSub: rising gravity only while rising with jump held."""
        if self.movement_state is MovementState.FALLING or self.velocity_y >= 0:
            self.gravity = self.falling_gravity
            return
        if controller.jump and self._jump_held_last_tick:
            return
        if self.jump_origin_y_pixels - self.pixel_y < JUMP_HALT_RISE_PIXELS:
            return
        self.gravity = self.falling_gravity

    def _move_horizontally(self, tiles: AttemptTiles) -> None:
        """Inside a solid tile, his box's edges don't stop him: his side probes
        push him out afterwards, as they stop him at every wall in the original."""
        if self.overlaps_solid_tile(tiles):
            self.x += self.whole_speed_x
        elif self.move_horizontally(tiles, self.whole_speed_x):
            self.velocity_x &= X_SUBSPEED_MASK

    def _move_vertically(self, tiles: AttemptTiles) -> None:
        """ImposeGravity, then the original's landing and head-bump responses."""
        contact = self.move_vertically(tiles, self.velocity_y)
        self.velocity_y = add_gravity(self.velocity_y, self.gravity, MARIO_TERMINAL_FALL_SPEED)
        if contact is VerticalContact.LANDED:
            self.velocity_y = 0
            self.movement_state = MovementState.ON_GROUND
        elif contact is VerticalContact.HIT_CEILING:
            self._hit_head_on((self.y >> SUBPIXEL_TO_TILE_SHIFT) - 1)

    def _hit_head_on(self, row: int) -> None:
        """His head hit the tile in this row over his centre: his rise stops."""
        self.velocity_y = HEAD_BUMP_SPEED + (self.velocity_y & Y_SUBSPEED_MASK)
        self.head_hit_tile = (self.centre_column, row)

    # --- PlayerBGCollision, once his box is inside a solid tile -------------------------------

    def _get_out_of_solid_tiles(self, tiles: AttemptTiles) -> None:
        """Growing or standing up can put his box inside a solid tile; elsewhere its
        edges keep him out, and these probes find nothing."""
        self._hit_head_from_inside(tiles)
        self._push_out_sideways(tiles)

    def _hit_head_from_inside(self, tiles: AttemptTiles) -> None:
        """HeadChk: rising with his head probe far enough into a solid tile, he hits it."""
        if self.velocity_y >= 0:
            return
        top_y_pixels = self.pixel_y
        row = top_y_pixels // TILE_SIZE_PIXELS
        if top_y_pixels % TILE_SIZE_PIXELS >= HEAD_PROBE_MIN_DEPTH_PIXELS and tiles.is_solid(self.centre_column, row):
            self._hit_head_on(row)

    def _push_out_sideways(self, tiles: AttemptTiles) -> None:
        """SideCheckLoop, ImpedePlayerMove: a probe on his left side inside a solid
        tile pushes him right, unless he is moving right; otherwise one on his right
        side pushes him left, unless he is moving left. A push stops him."""
        left_x_pixels = self.pixel_x
        right_x_pixels = (self.x + self.width - 1) >> SUBPIXEL_BITS
        if self._side_probe_is_in_solid_tile(tiles, left_x_pixels):
            if self.whole_speed_x <= 0:
                self._push_sideways(SIDE_PUSH_PIXELS)
        elif self._side_probe_is_in_solid_tile(tiles, right_x_pixels) and self.whole_speed_x >= 0:
            self._push_sideways(-SIDE_PUSH_PIXELS)

    def _side_probe_is_in_solid_tile(self, tiles: AttemptTiles, x_pixels: int) -> bool:
        sprite_y_pixels = self.pixel_y - self.hitbox_offset_y_pixels
        column = x_pixels // TILE_SIZE_PIXELS
        return any(tiles.is_solid(column, (sprite_y_pixels + probe_y_pixels) // TILE_SIZE_PIXELS)
                   for probe_y_pixels in SIDE_PROBE_SPRITE_Y_PIXELS[self._body])

    def _push_sideways(self, distance_pixels: int) -> None:
        self.x += distance_pixels * SUBPIXELS_PER_PIXEL
        self.velocity_x &= X_SUBSPEED_MASK
