"""py -m mario train [config]: headless training of one run, recorded in its run folder
(spec sections 2, 9 and 10, ADR 0001).

This is the only place that imports the user's package, through the one fixed
import `from neuroevolution import create_algorithm`. If the package is missing
or broken, training stops with a message saying so instead of a traceback, and
before any run folder is made.
"""

from datetime import datetime
from pathlib import Path

from mario.recording.run_recorder import RunRecorder
from mario.training.agent_worker_pool import AgentWorkerPool, WorkerStartError
from mario.training.algorithm_factory import AlgorithmFactory, CreateAlgorithm
from mario.training.generation_printer import GenerationPrinter
from mario.training.generation_recorder import GenerationRecorder
from mario.training.neuroevolution_algorithm import NeuroevolutionAlgorithm
from mario.training.run_config import RunConfig
from mario.training.trainer import Trainer

NOT_READY_MESSAGE = ("The learning algorithm isn't ready: {problem}.\n"
                     "Training needs the neuroevolution package at the repo root, exposing "
                     "create_algorithm(settings) that returns a NeuroevolutionAlgorithm.")
RUN_ALREADY_STARTED_MESSAGE = "A run named {run_name!r} already started this minute: {run_folder}"


class TrainMode:
    def __init__(self, config_path: Path, runs_root: Path):
        """runs_root: the folder the run's own run folder is made in."""
        self._config_path = config_path
        self._runs_root = runs_root

    def run(self) -> None:
        try:
            config = RunConfig.load(self._config_path)
        except (OSError, ValueError) as problem:
            raise SystemExit(f"Can't read the run's config: {problem}") from None
        algorithm_factory = AlgorithmFactory(_import_create_algorithm(), config.algorithm_settings)
        algorithm = _create_algorithm(algorithm_factory)
        try:
            worker_pool = AgentWorkerPool(algorithm_factory)
        except WorkerStartError as problem:  # it built here, but not in a worker
            raise SystemExit(_not_ready(f"neuroevolution's {problem}")) from None
        with worker_pool:
            run_recorder = self._start_recording(config.run.name)
            Trainer(algorithm, worker_pool, config.run,
                    [GenerationRecorder(run_recorder), GenerationPrinter()]).run()

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
