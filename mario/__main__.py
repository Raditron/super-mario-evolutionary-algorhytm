"""py -m mario play"""

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(prog="py -m mario", description="Mario World 1-1 neuroevolution")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("play", help="play World 1-1 with the keyboard")
    arguments = parser.parse_args()
    if arguments.command == "play":
        from mario.modes.play_mode import PlayMode
        PlayMode.with_keyboard().run()


if __name__ == "__main__":
    main()
