"""Which Controller buttons are held on one tick, read from the bitmask."""

from mario.constants.controller import CONTROLLER_BUTTONS

LEFT_MASK = 1 << CONTROLLER_BUTTONS.index("left")
RIGHT_MASK = 1 << CONTROLLER_BUTTONS.index("right")
DOWN_MASK = 1 << CONTROLLER_BUTTONS.index("down")
JUMP_MASK = 1 << CONTROLLER_BUTTONS.index("jump")
RUN_MASK = 1 << CONTROLLER_BUTTONS.index("run")
ALL_BUTTONS_MASK = (1 << len(CONTROLLER_BUTTONS)) - 1

RIGHT = 1
LEFT = -1
NO_DIRECTION = 0


class ControllerState:
    """One tick of the Controller. Left and right held together count as
    neither held, like a real d-pad that cannot press both."""

    __slots__ = ("direction", "down", "jump", "run", "holds_any_button_but_jump")

    def __init__(self, buttons: int):
        if buttons & ~ALL_BUTTONS_MASK:
            raise ValueError(f"not a Controller bitmask: {buttons}")
        if buttons & LEFT_MASK and buttons & RIGHT_MASK:
            buttons &= ~(LEFT_MASK | RIGHT_MASK)
        if buttons & RIGHT_MASK:
            self.direction = RIGHT
        elif buttons & LEFT_MASK:
            self.direction = LEFT
        else:
            self.direction = NO_DIRECTION
        self.down = bool(buttons & DOWN_MASK)
        self.jump = bool(buttons & JUMP_MASK)
        self.run = bool(buttons & RUN_MASK)
        self.holds_any_button_but_jump = bool(buttons & ~JUMP_MASK)

    @staticmethod
    def bitmask(left: bool = False, right: bool = False, down: bool = False,
                jump: bool = False, run: bool = False) -> int:
        return ((LEFT_MASK if left else 0) | (RIGHT_MASK if right else 0)
                | (DOWN_MASK if down else 0) | (JUMP_MASK if jump else 0)
                | (RUN_MASK if run else 0))
