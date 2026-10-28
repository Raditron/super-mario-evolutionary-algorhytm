"""py -m mario play | train [config] | replay <run-folder> [--generation N] --best"""

import argparse
from pathlib import Path

from mario.constants.recording import RUNS_FOLDER_NAME
from mario.constants.training import DEFAULT_CONFIG_FILE_NAME
from mario.constants.view import SPRITES_FOLDER_PARTS

REPO_ROOT = Path(__file__).parent.parent
# config.toml sits at the repo root, next to the mario package.
DEFAULT_CONFIG_PATH = REPO_ROOT / DEFAULT_CONFIG_FILE_NAME
# Run folders are made in runs/ at the repo root, whatever folder train is run from.
RUNS_ROOT = REPO_ROOT / RUNS_FOLDER_NAME
# The Sprite view's PNGs are in assets/sprites/ at the repo root.
SPRITES_FOLDER = REPO_ROOT.joinpath(*SPRITES_FOLDER_PARTS)
ALL_GHOST_REPLAY_NOT_BUILT_MESSAGE = ("Replaying every agent of a generation as ghosts isn't built yet (#30); "
                                      "pass --best to replay its best agent.")


def main(runs_root: Path = RUNS_ROOT) -> None:
    """runs_root: where train makes its run folder; tests pass a folder of their own."""
    parser = argparse.ArgumentParser(prog="py -m mario", description="Mario World 1-1 neuroevolution")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("play", help="play World 1-1 with the keyboard")
    train_parser = commands.add_parser("train", help="train one run headless")
    train_parser.add_argument("config", nargs="?", type=Path, default=DEFAULT_CONFIG_PATH,
                              help=f"the run's settings (default: {DEFAULT_CONFIG_FILE_NAME} at the repo root)")
    replay_parser = commands.add_parser("replay", help="replay a recorded generation")
    replay_parser.add_argument("run_folder", type=Path, help="the run's folder, in runs/")
    replay_parser.add_argument("--generation", type=int, default=None,
                               help="the generation to replay (default: the last one recorded)")
    replay_parser.add_argument("--best", action="store_true", help="replay only the generation's best agent")
    arguments = parser.parse_args()
    if arguments.command == "play":
        from mario.modes.play_mode import PlayMode
        PlayMode.with_keyboard(SPRITES_FOLDER).run()
    elif arguments.command == "train":
        from mario.modes.train_mode import TrainMode
        TrainMode(arguments.config, runs_root).run()
    elif arguments.command == "replay":
        if not arguments.best:
            raise SystemExit(ALL_GHOST_REPLAY_NOT_BUILT_MESSAGE)
        from mario.modes.replay_mode import ReplayMode
        ReplayMode.of_best_agent(arguments.run_folder, arguments.generation, SPRITES_FOLDER).run()


if __name__ == "__main__":
    main()
