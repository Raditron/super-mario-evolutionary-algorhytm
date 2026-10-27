"""py -m mario play | train [config]"""

import argparse
from pathlib import Path

from mario.constants.recording import RUNS_FOLDER_NAME
from mario.constants.training import DEFAULT_CONFIG_FILE_NAME

# config.toml sits at the repo root, next to the mario package.
DEFAULT_CONFIG_PATH = Path(__file__).parent.parent / DEFAULT_CONFIG_FILE_NAME
# Run folders are made in runs/ of the folder train is run from: the repo root, where py -m mario runs.
RUNS_ROOT = Path(RUNS_FOLDER_NAME)


def main() -> None:
    parser = argparse.ArgumentParser(prog="py -m mario", description="Mario World 1-1 neuroevolution")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("play", help="play World 1-1 with the keyboard")
    train_parser = commands.add_parser("train", help="train one run headless")
    train_parser.add_argument("config", nargs="?", type=Path, default=DEFAULT_CONFIG_PATH,
                              help=f"the run's settings (default: {DEFAULT_CONFIG_FILE_NAME} at the repo root)")
    arguments = parser.parse_args()
    if arguments.command == "play":
        from mario.modes.play_mode import PlayMode
        PlayMode.with_keyboard().run()
    elif arguments.command == "train":
        from mario.modes.train_mode import TrainMode
        TrainMode(arguments.config, RUNS_ROOT).run()


if __name__ == "__main__":
    main()
