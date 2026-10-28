"""py -m mario train [config] [--watch]: training of one run, recorded in its run folder
(spec sections 2, 9, 10 and 11, ADR 0001). Headless unless watched; watched, each
generation is shown live in a window, and closing it stops the run, leaving its
folder with only the generations finished before.

This is the only place that imports the user's package, through the one fixed
import `from neuroevolution import create_algorithm`. If the package is missing
or broken, training stops with a message saying so instead of a traceback, and
before any run folder is made.

The window is imported only when watched, so headless training never loads pygame.
"""

from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from mario.recording.run_recorder import RunRecorder
from mario.training.agent_worker_pool import AgentWorkerPool, WorkerStartError
from mario.training.algorithm_factory import AlgorithmFactory, CreateAlgorithm
from mario.training.generation_printer import GenerationPrinter
from mario.training.generation_recorder import GenerationRecorder
from mario.training.neuroevolution_algorithm import NeuroevolutionAlgorithm
from mario.training.play_watcher import ViewerClosed
from mario.training.run_config import RunConfig
from mario.training.trainer import Trainer

if TYPE_CHECKING:
    from mario.modes.watch_live import WatchLive

NOT_READY_MESSAGE = ("The learning algorithm isn't ready: {problem}.\n"
                     "Training needs the neuroevolution package at the repo root, exposing "
                     "create_algorithm(settings) that returns a NeuroevolutionAlgorithm.")
RUN_ALREADY_STARTED_MESSAGE = "A run named {run_name!r} already started this minute: {run_folder}"
WINDOW_CLOSED_MESSAGE = ("The window was closed, so training stopped; {run_folder} keeps "
                         "the generations finished before.")


class TrainMode:
    def __init__(self, config_path: Path, runs_root: Path, watch: bool = False, sprites_folder: Path | None = None):
        """runs_root: the folder the run's own run folder is made in. watch: show each
        generation live, its Sprite view reading its PNGs from sprites_folder."""
        self._config_path = config_path
        self._runs_root = runs_root
        self._watch = watch
        self._sprites_folder = sprites_folder

    def run(self) -> None:
        try:
            config = RunConfig.load(self._config_path)
        except (OSError, ValueError) as problem:
            raise SystemExit(f"Can't read the run's config: {problem}") from None
        algorithm_factory = AlgorithmFactory(_import_create_algorithm(), config.algorithm_settings)
        algorithm = _create_algorithm(algorithm_factory)
        watch_live = self._watch_live() if self._watch else None
        try:
            try:
                worker_pool = AgentWorkerPool(algorithm_factory, play_watcher=watch_live)
            except WorkerStartError as problem:  # it built here, but not in a worker
                raise SystemExit(_not_ready(f"neuroevolution's {problem}")) from None
            try:  # the window opens, and so can be closed, only once the run is recording
                with worker_pool:  # left by ViewerClosed, it stops the workers rather than waiting for them
                    run_recorder = self._start_recording(config.run.name)
                    Trainer(algorithm, worker_pool, config.run,
                            [GenerationRecorder(run_recorder), GenerationPrinter()]).run()
            except ViewerClosed:
                print(WINDOW_CLOSED_MESSAGE.format(run_folder=run_recorder.run_folder_path), flush=True)
        finally:
            if watch_live is not None:
                watch_live.close()

    def _watch_live(self) -> "WatchLive":
        from mario.modes.watch_live import WatchLive  # only watched training loads pygame
        return WatchLive.in_a_window(self._sprites_folder)

    def _start_recording(self, run_name: str) -> RunRecorder:
        """Make the run folder: only once the algorithm has built here and in every worker."""
        try:
            return RunRecorder.start(self._runs_root, run_name, self._config_path, datetime.now())
        except FileExistsError as problem:
            raise SystemExit(RUN_ALREADY_STARTED_MESSAGE.format(
                run_name=run_name, run_folder=problem.filename)) from None


def _import_create_algorithm() -> CreateAlgorithm:
    try:
        from neuroevolution import create_algorithm
    except Exception as problem:  # a half-written package can fail in any way on import
        raise SystemExit(_not_ready(f"`from neuroevolution import create_algorithm` failed "
                                    f"({type(problem).__name__}: {problem})")) from None
    return create_algorithm


def _create_algorithm(algorithm_factory: AlgorithmFactory) -> NeuroevolutionAlgorithm:
    try:
        algorithm = algorithm_factory.create()
    except Exception as problem:  # the user's code, half-written
        raise SystemExit(_not_ready(f"neuroevolution's create_algorithm(settings) failed "
                                    f"({type(problem).__name__}: {problem})")) from None
    if not isinstance(algorithm, NeuroevolutionAlgorithm):
        raise SystemExit(_not_ready(f"neuroevolution's create_algorithm(settings) returned a "
                                    f"{type(algorithm).__name__}, not a NeuroevolutionAlgorithm"))
    return algorithm


def _not_ready(problem: str) -> str:
    return NOT_READY_MESSAGE.format(problem=problem)
