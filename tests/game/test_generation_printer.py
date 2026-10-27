"""The one line train mode prints per generation (#26)."""

import numpy as np

from mario.training.generation_printer import GenerationPrinter
from mario.training.trainer import GenerationReport


def test_each_generation_prints_one_line_with_best_and_mean_fitness_and_seconds(capsys):
    report = GenerationReport(generation=3, genomes=[], played_attempts=[],
                              fitnesses=np.array([1.0, 2.0, 6.5]), seconds=1.234)
    GenerationPrinter().generation_finished(report)
    assert capsys.readouterr().out == "generation 3 · best fitness 6.50 · mean fitness 3.17 · 1.23 s\n"
