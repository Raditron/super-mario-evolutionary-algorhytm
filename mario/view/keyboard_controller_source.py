"""Play mode's Controller: the keys held right now."""

import pygame

from mario.constants.view import KEYBOARD_BUTTON_KEYS
from mario.controller.controller_source import ControllerSource
from mario.controller.controller_state import ControllerState


class KeyboardControllerSource(ControllerSource):
    def __init__(self):
        self._key_codes = {button: pygame.key.key_code(key_name)
                           for button, key_name in KEYBOARD_BUTTON_KEYS.items()}

    def next_buttons(self) -> int:
        pressed = pygame.key.get_pressed()
        return ControllerState.bitmask(**{button: pressed[key_code]
                                          for button, key_code in self._key_codes.items()})
