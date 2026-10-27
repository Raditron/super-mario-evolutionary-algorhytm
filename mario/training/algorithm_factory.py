"""How every process builds the user's algorithm: create_algorithm(settings), as one picklable value."""

from collections.abc import Callable
from dataclasses import dataclass

from mario.training.neuroevolution_algorithm import NeuroevolutionAlgorithm

# The user's package exposes one of these as neuroevolution.create_algorithm.
CreateAlgorithm = Callable[[dict], NeuroevolutionAlgorithm]


@dataclass(frozen=True)
class AlgorithmFactory:
    """create_algorithm must be importable by name (a module-level function), since
    each worker process unpickles it to build its own algorithm."""
    create_algorithm: CreateAlgorithm
    settings: dict

    def create(self) -> NeuroevolutionAlgorithm:
        return self.create_algorithm(self.settings)
