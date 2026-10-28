"""Training's side of recording: each finished generation goes into the run folder.

The recorder knows only AttemptResults, Controller logs, floats and flat arrays,
so this listener takes the generation report apart for it.
"""

from mario.recording.run_recorder import RunRecorder
from mario.training.trainer import GenerationListener, GenerationReport


class GenerationRecorder(GenerationListener):
    def __init__(self, run_recorder: RunRecorder):
        self._run_recorder = run_recorder

    def generation_finished(self, report: GenerationReport) -> None:
        self._run_recorder.record_generation(
            report.generation,
            [played_attempt.attempt_result for played_attempt in report.played_attempts],
            [played_attempt.controller_log for played_attempt in report.played_attempts],
            report.fitnesses, report.genomes, report.seconds)
