"""py -m mario train [config]: headless training of one run (spec sections 2 and 9, ADR 0001).

This is the only place that imports the user's package, through the one fixed
import `from neuroevolution import create_algorithm`. If the package is missing
or broken, training stops with a message saying so instead of a traceback.
"""

from pathlib import Path

from mario.training.agent_worker_pool import AgentWorkerPool
from mario.training.algorithm_factory import AlgorithmFactory, CreateAlgorithm
from mario.training.generation_printer import GenerationPrinter
from mario.training.neuroevolution_algorithm import NeuroevolutionAlgorithm
from mario.training.run_config import RunConfig
from mario.training.trainer import Trainer

NOT_READY_MESSAGE = ("The learning algorithm isn't ready: {problem}.\n"
                     "Training needs the neuroevolution package at the repo root, exposing "
                     "create_algorithm(settings) that returns a NeuroevolutionAlgorithm.")


class TrainMode:
    def __init__(self, config_path: Path):
        self._config_path = config_path

    def run(self) -> None:
        try:
            config = RunConfig.load(self._config_path)
        except (OSError, ValueError) as problem:
            raise SystemExit(f"Can't read the run's config: {problem}") from None
        algorithm_factory = AlgorithmFactory(_import_create_algorithm(), config.algorithm_settings)
        algorithm = _create_algorithm(algorithm_factory)
        with AgentWorkerPool(algorithm_factory) as worker_pool:
            Trainer(algorithm, worker_pool, config.run, GenerationPrinter()).run()


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
