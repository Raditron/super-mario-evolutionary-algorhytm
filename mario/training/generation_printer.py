"""Headless training's progress: one printed line per generation."""

from mario.constants.training import PRINTED_FITNESS_DECIMALS, PRINTED_SECONDS_DECIMALS
from mario.training.trainer import GenerationListener, GenerationReport


class GenerationPrinter(GenerationListener):
    def generation_finished(self, report: GenerationReport) -> None:
        print(f"generation {report.generation}"
              f" · best fitness {report.fitnesses.max():.{PRINTED_FITNESS_DECIMALS}f}"
              f" · mean fitness {report.fitnesses.mean():.{PRINTED_FITNESS_DECIMALS}f}"
              f" · {report.seconds:.{PRINTED_SECONDS_DECIMALS}f} s", flush=True)
