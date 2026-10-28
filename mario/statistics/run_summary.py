"""summary.txt (spec section 13): a run's headline facts, computed from its rows every time, never stored."""

from dataclasses import dataclass

from mario.constants.physics import TICKS_PER_SECOND
from mario.constants.statistics import (
    AGENT_OF_A_VALUE_FORMAT,
    BEST_FITNESS_LABEL,
    FASTEST_FINISH_LABEL,
    FINISH_TIME_FORMAT,
    FIRST_FLAG_GENERATION_LABEL,
    MOST_COINS_LABEL,
    NEVER_REACHED_THE_FLAG_TEXT,
    REACHED_FLAG_END_REASON,
    SECONDS_FORMAT,
    SUMMARY_FITNESS_DECIMALS,
    SUMMARY_LINE_FORMAT,
    SUMMARY_SECONDS_DECIMALS,
    TOTAL_RUN_TIME_LABEL,
)
from mario.recording.best_agent import best_agent_index
from mario.recording.generation_time_row import GenerationTimeRow
from mario.recording.results_row import ResultsRow


@dataclass(frozen=True)
class RunSummary:
    """Each fact's row is the earliest one that holds it: on a tie, the lowest
    generation, then the lowest agent index. The flag facts are None if no agent reached it."""
    first_flag_generation: int | None
    best_fitness_row: ResultsRow
    fastest_finish_row: ResultsRow | None
    most_coins_row: ResultsRow
    total_seconds: float

    @classmethod
    def of(cls, results_rows: list[ResultsRow], generation_time_rows: list[GenerationTimeRow]) -> "RunSummary":
        """results_rows: at least one."""
        rows = sorted(results_rows, key=lambda row: (row.generation, row.agent_index))
        finishers = [row for row in rows if row.end_reason == REACHED_FLAG_END_REASON]
        return cls(
            first_flag_generation=finishers[0].generation if finishers else None,
            best_fitness_row=_earliest_highest(rows, [row.fitness for row in rows]),
            fastest_finish_row=_earliest_highest(finishers, [-row.ticks_elapsed for row in finishers])
            if finishers else None,
            most_coins_row=_earliest_highest(rows, [row.coins_collected for row in rows]),
            total_seconds=sum(row.seconds for row in generation_time_rows))

    def entries(self) -> list[tuple[str, str]]:
        """Each fact's label and its value as text, in the order summary.txt lists them."""
        best_fitness = f"{self.best_fitness_row.fitness:.{SUMMARY_FITNESS_DECIMALS}f}"
        return [
            (FIRST_FLAG_GENERATION_LABEL, NEVER_REACHED_THE_FLAG_TEXT if self.first_flag_generation is None
             else str(self.first_flag_generation)),
            (BEST_FITNESS_LABEL, _of_its_agent(best_fitness, self.best_fitness_row)),
            (FASTEST_FINISH_LABEL, self._fastest_finish_text()),
            (MOST_COINS_LABEL, _of_its_agent(str(self.most_coins_row.coins_collected), self.most_coins_row)),
            (TOTAL_RUN_TIME_LABEL, _seconds_text(self.total_seconds)),
        ]

    def text(self) -> str:
        """summary.txt: one line per fact."""
        return "".join(SUMMARY_LINE_FORMAT.format(label=label, value=value) + "\n" for label, value in self.entries())

    def _fastest_finish_text(self) -> str:
        if self.fastest_finish_row is None:
            return NEVER_REACHED_THE_FLAG_TEXT
        ticks = self.fastest_finish_row.ticks_elapsed
        finish_time = FINISH_TIME_FORMAT.format(seconds=_seconds_text(ticks / TICKS_PER_SECOND), ticks=ticks)
        return _of_its_agent(finish_time, self.fastest_finish_row)


def _earliest_highest(rows: list[ResultsRow], values: list[float]) -> ResultsRow:
    """The row with the highest value; on a tie, the first, as the best-agent rule picks."""
    return rows[best_agent_index(values)]


def _of_its_agent(value: str, row: ResultsRow) -> str:
    return AGENT_OF_A_VALUE_FORMAT.format(value=value, generation=row.generation, agent=row.agent_index)


def _seconds_text(seconds: float) -> str:
    return SECONDS_FORMAT.format(seconds=seconds, decimals=SUMMARY_SECONDS_DECIMALS)
