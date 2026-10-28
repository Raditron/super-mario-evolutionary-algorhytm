"""One row of results.csv (spec section 10): written by the RunRecorder, read back by RecordedRun."""

from dataclasses import astuple, dataclass, fields

from mario.constants.recording import RESULTS_COLUMNS
from mario.simulation.attempt_result import AttemptResult, EndReason


@dataclass(frozen=True)
class ResultsRow:
    """One agent's row: its fitness and its attempt's end-of-attempt facts.

    Its fields are the RESULTS_COLUMNS, in their order, each typed as its column is read back."""
    generation: int
    agent_index: int
    fitness: float
    end_reason: EndReason
    furthest_x: int
    ticks_elapsed: int
    final_score: int
    coins_collected: int

    @classmethod
    def of(cls, generation: int, agent_index: int, fitness: float, attempt_result: AttemptResult) -> "ResultsRow":
        return cls(generation, agent_index, float(fitness), attempt_result.end_reason, attempt_result.furthest_x,
                   attempt_result.ticks_elapsed, attempt_result.final_score, attempt_result.coins_collected)

    @classmethod
    def parse(cls, row: dict[str, str]) -> "ResultsRow":
        """A row as csv.DictReader reads it, keyed by the RESULTS_COLUMNS."""
        return cls(*(field.type(row[column]) for field, column in zip(fields(cls), RESULTS_COLUMNS, strict=True)))

    def csv_values(self) -> tuple:
        """The row's values in the order of the RESULTS_COLUMNS."""
        return astuple(self)
