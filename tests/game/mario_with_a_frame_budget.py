"""`py -m mario <arguments>`, with the window closed for it after a number of frames.

Run as a script by the tests of the modes that hold their last frame until the
viewer quits: closing the window is the viewer's part, done here by posting
pygame's QUIT event once the frame budget is spent. Run folders `train` makes
go into runs/ of the folder it runs in, not the repo root's. At the end it
prints how many frames were shown and whether the user's neuroevolution
package was imported.

    py tests/game/mario_with_a_frame_budget.py <frame-budget> <py -m mario arguments...>
"""

import sys
from pathlib import Path

import pygame

from mario.__main__ import main as mario_main

FRAMES_SHOWN_PREFIX = "frames shown: "
NEUROEVOLUTION_IMPORTED_PREFIX = "neuroevolution imported: "


def main() -> None:
    frame_budget = int(sys.argv[1])
    mario_arguments = sys.argv[2:]
    frames_shown = 0
    show_frame = pygame.display.flip

    def show_frame_then_close_once_the_budget_is_spent() -> None:
        nonlocal frames_shown
        show_frame()
        frames_shown += 1
        if frames_shown == frame_budget:
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    pygame.display.flip = show_frame_then_close_once_the_budget_is_spent
    sys.argv = ["mario", *mario_arguments]
    mario_main(runs_root=Path("runs"))
    print(f"{FRAMES_SHOWN_PREFIX}{frames_shown}")
    print(f"{NEUROEVOLUTION_IMPORTED_PREFIX}{'neuroevolution' in sys.modules}")


if __name__ == "__main__":
    main()
