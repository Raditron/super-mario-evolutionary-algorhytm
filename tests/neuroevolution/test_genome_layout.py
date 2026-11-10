"""Milestone 3: a genome is W1, b1, W2, b2 laid end to end, and the layout can go both ways."""

import numpy as np
import pytest

from neuroevolution.constants import INPUT_SIZE, OUTPUT_SIZE
from neuroevolution.genome_layout import GenomeLayout

HIDDEN_LAYER_SIZE = 24
REAL_LAYOUT_SIZES = [INPUT_SIZE, HIDDEN_LAYER_SIZE, OUTPUT_SIZE]
REAL_GENE_COUNT = 3989  # 160*24 + 24 + 24*5 + 5

TINY_LAYOUT_SIZES = [2, 2, 1]
TINY_GENE_COUNT = 9  # 2*2 + 2 + 2*1 + 1
COUNTING_GENOME = np.arange(TINY_GENE_COUNT, dtype=np.float64)

SEED_FOR_THE_RANDOM_GENOME = 3


def test_the_real_layout_holds_3989_genes():
    assert GenomeLayout(REAL_LAYOUT_SIZES).gene_count == REAL_GENE_COUNT


def test_the_tiny_layout_holds_nine_genes():
    assert GenomeLayout(TINY_LAYOUT_SIZES).gene_count == TINY_GENE_COUNT


def test_a_counting_genome_puts_each_number_in_its_place():
    (hidden_weights, hidden_biases), (output_weights, output_biases) = GenomeLayout(TINY_LAYOUT_SIZES).unpack(
        COUNTING_GENOME
    )

    # W1 is flattened row by row: 0, 1 is the first input's row, 2, 3 the second's.
    assert hidden_weights.tolist() == [[0.0, 1.0], [2.0, 3.0]]
    assert hidden_biases.tolist() == [4.0, 5.0]
    assert output_weights.tolist() == [[6.0], [7.0]]
    assert output_biases.tolist() == [8.0]


def test_the_unpacked_shapes_match_the_real_network():
    (hidden_weights, hidden_biases), (output_weights, output_biases) = GenomeLayout(REAL_LAYOUT_SIZES).unpack(
        np.zeros(REAL_GENE_COUNT)
    )

    assert hidden_weights.shape == (INPUT_SIZE, HIDDEN_LAYER_SIZE)
    assert hidden_biases.shape == (HIDDEN_LAYER_SIZE,)
    assert output_weights.shape == (HIDDEN_LAYER_SIZE, OUTPUT_SIZE)
    assert output_biases.shape == (OUTPUT_SIZE,)


def test_packing_what_was_unpacked_gives_the_same_genome_back():
    layout = GenomeLayout(REAL_LAYOUT_SIZES)
    genome = np.random.default_rng(SEED_FOR_THE_RANDOM_GENOME).standard_normal(REAL_GENE_COUNT)

    round_tripped = layout.pack(layout.unpack(genome))

    assert np.array_equal(round_tripped, genome)


def test_packing_puts_each_number_in_its_place():
    layers_parameters = [
        (np.array([[0.0, 1.0], [2.0, 3.0]]), np.array([4.0, 5.0])),
        (np.array([[6.0], [7.0]]), np.array([8.0])),
    ]

    genome = GenomeLayout(TINY_LAYOUT_SIZES).pack(layers_parameters)

    assert genome.tolist() == COUNTING_GENOME.tolist()


def test_a_genome_of_the_wrong_length_is_refused():
    layout = GenomeLayout(TINY_LAYOUT_SIZES)

    with pytest.raises(ValueError, match="genes"):
        layout.unpack(np.zeros(TINY_GENE_COUNT + 1))
