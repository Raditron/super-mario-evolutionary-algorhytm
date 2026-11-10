"""Milestone 3: the one fixed rule for turning a genome (a flat 1-D float array) into weights and biases, and back."""

import numpy as np

# One layer's numbers: (weights, biases). weights has one row per input and one column per neuron.
LayerParameters = tuple[np.ndarray, np.ndarray]


class GenomeLayout:
    """layer_sizes is the neuron count of each stage, e.g. [160, 24, 5]: the inputs, then every layer.

    A genome holds each layer's weights (flattened row by row), then that layer's biases, layer after layer:
    W1, b1, W2, b2.
    """

    def __init__(self, layer_sizes: list[int]) -> None:
        self._layer_sizes = layer_sizes

    @property
    def gene_count(self) -> int:
        """How many numbers one genome holds."""
        count: int = 0
        for layer_index in range(len(self._layer_sizes) - 1):
            input_count = self._layer_sizes[layer_index]
            neuron_count = self._layer_sizes[layer_index + 1]
            count += input_count * neuron_count + neuron_count
        return count


    def unpack(self, genome: np.ndarray) -> list[LayerParameters]:
        """A flat genome -> one (weights, biases) pair per layer."""
        if len(genome) != self.gene_count:
            raise ValueError(
                f"Genome has {len(genome)} genes, but {self.gene_count} are expected"
            )

        layers_parameters: list[LayerParameters] = []
        position = 0
        for layer_index in range(len(self._layer_sizes) - 1):
            input_count = self._layer_sizes[layer_index]
            neuron_count = self._layer_sizes[layer_index + 1]

            weight_count = input_count * neuron_count
            weights = genome[position : position + weight_count].reshape(
                input_count, neuron_count
            )
            position += weight_count

            biases = genome[position : position + neuron_count]
            position += neuron_count

            layers_parameters.append((weights, biases))
        return layers_parameters

    def pack(self, layers_parameters: list[LayerParameters]) -> np.ndarray:
        """One (weights, biases) pair per layer -> a flat genome. The exact reverse of unpack."""
        pieces: list[np.ndarray] = []
        for weights, biases in layers_parameters: 
            pieces.append(weights.ravel())
            pieces.append(biases)
        return np.concatenate(pieces)        
