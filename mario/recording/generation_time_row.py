"""One row of generation_times.csv (spec section 10): written by the RunRecorder, read back by RecordedRun."""

from dataclasses import astuple, dataclass, fields

from mario.constants.recording import GENERATION_TIMES_COLUMNS


@dataclass(frozen=True)
class GenerationTimeRow:
    """One generation's wall-clock seconds: playing and scoring it, not recording it.

    Its fields are the GENERATION_TIMES_COLUMNS, in their order, each typed as its column is read back."""
    generation: int
    seconds: float

    @classmethod
    def parse(cls, row: dict[str, str]) -> "GenerationTimeRow":
        """A row as csv.DictReader reads it, keyed by the GENERATION_TIMES_COLUMNS."""
        return cls(*(field.type(row[column])
                     for field, column in zip(fields(cls), GENERATION_TIMES_COLUMNS, strict=True)))

    def csv_values(self) -> tuple:
        """The row's values in the order of the GENERATION_TIMES_COLUMNS."""
        return astuple(self)
