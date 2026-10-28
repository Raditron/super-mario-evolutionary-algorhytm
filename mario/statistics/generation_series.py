"""What the charts of spec section 13 plot: one value per generation, computed from a run's rows every time."""

from dataclasses import dataclass

import numpy as np

from mario.constants.physics import TICKS_PER_SECOND
from mario.constants.statistics import (
    END_REASON_COLOURS,
    FITNESS_BAND_HIGH_PERCENTILE,
    FITNESS_BAND_LOW_PERCENTILE,
    HEATMAP_BIN_WIDTH_PIXELS,
    HEATMAP_LEVEL_WIDTH_PIXELS,
    REACHED_FLAG_END_REASON,
)
from mario.recording.generation_time_row import GenerationTimeRow
from mario.recording.results_row import ResultsRow


@dataclass(frozen=True)
class GenerationSeries:
    """Every array but the timed ones lines up with generations, in increasing order."""
    generations: np.ndarray
    best_fitness: np.ndarray
    mean_fitness: np.ndarray
    median_fitness: np.ndarray
    fitness_band_low: np.ndarray
    fitness_band_high: np.ndarray
    best_furthest_x: np.ndarray
    median_furthest_x: np.ndarray
    # Each end_reason's share of the generation's attempts, keyed in END_REASON_COLOURS' order.
    end_reason_shares: dict[str, np.ndarray]
    # How many attempts of each generation (column) reached each furthest_x bin (row);
    # heatmap_bin_edges are the bins' edges in pixels.
    furthest_x_counts: np.ndarray
    heatmap_bin_edges: np.ndarray
    best_coins: np.ndarray
    mean_coins: np.ndarray
    # The fewest seconds any agent of the generation took to reach the flag: NaN where none did.
    fastest_flag_seconds: np.ndarray
    # generation_times.csv: its generations and each one's wall-clock seconds.
    timed_generations: np.ndarray
    seconds_per_generation: np.ndarray

    @classmethod
    def of(cls, results_rows: list[ResultsRow], generation_time_rows: list[GenerationTimeRow]) -> "GenerationSeries":
        """results_rows: at least one."""
        generations = np.array(sorted({row.generation for row in results_rows}))
        rows_by_generation = [[row for row in results_rows if row.generation == generation]
                              for generation in generations]
        fitnesses = [np.array([row.fitness for row in rows]) for rows in rows_by_generation]
        furthest_xs = [np.array([row.furthest_x for row in rows]) for rows in rows_by_generation]
        coins = [np.array([row.coins_collected for row in rows]) for rows in rows_by_generation]
        heatmap_bin_edges = np.arange(0, HEATMAP_LEVEL_WIDTH_PIXELS + HEATMAP_BIN_WIDTH_PIXELS,
                                      HEATMAP_BIN_WIDTH_PIXELS)
        timed_rows = sorted(generation_time_rows, key=lambda row: row.generation)
        return cls(
            generations=generations,
            best_fitness=np.array([values.max() for values in fitnesses]),
            mean_fitness=np.array([values.mean() for values in fitnesses]),
            median_fitness=np.array([np.median(values) for values in fitnesses]),
            fitness_band_low=np.array([np.percentile(values, FITNESS_BAND_LOW_PERCENTILE) for values in fitnesses]),
            fitness_band_high=np.array([np.percentile(values, FITNESS_BAND_HIGH_PERCENTILE) for values in fitnesses]),
            best_furthest_x=np.array([values.max() for values in furthest_xs]),
            median_furthest_x=np.array([np.median(values) for values in furthest_xs]),
            end_reason_shares={end_reason: np.array([_share(rows, end_reason) for rows in rows_by_generation])
                               for end_reason in END_REASON_COLOURS},
            furthest_x_counts=np.column_stack([_furthest_x_counts(values, heatmap_bin_edges)
                                               for values in furthest_xs]),
            heatmap_bin_edges=heatmap_bin_edges,
            best_coins=np.array([values.max() for values in coins]),
            mean_coins=np.array([values.mean() for values in coins]),
            fastest_flag_seconds=np.array([_fastest_flag_seconds(rows) for rows in rows_by_generation]),
            timed_generations=np.array([row.generation for row in timed_rows]),
            seconds_per_generation=np.array([row.seconds for row in timed_rows]))

    @property
    def anyone_reached_the_flag(self) -> bool:
        return bool(np.any(~np.isnan(self.fastest_flag_seconds)))


def _share(rows: list[ResultsRow], end_reason: str) -> float:
    return sum(row.end_reason == end_reason for row in rows) / len(rows)


def _furthest_x_counts(furthest_xs: np.ndarray, bin_edges: np.ndarray) -> np.ndarray:
    """Attempts beyond the last bin count in it."""
    return np.histogram(np.clip(furthest_xs, bin_edges[0], bin_edges[-1] - 1), bins=bin_edges)[0]


def _fastest_flag_seconds(rows: list[ResultsRow]) -> float:
    finish_ticks = [row.ticks_elapsed for row in rows if row.end_reason == REACHED_FLAG_END_REASON]
    return min(finish_ticks) / TICKS_PER_SECOND if finish_ticks else np.nan
