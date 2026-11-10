"""Two tiny 2 -> 2 -> 1 networks with weights chosen so the answers can be worked out by hand."""

import numpy as np

from neuroevolution.layer import Layer
from neuroevolution.neural_network import NeuralNetwork

TINY_INPUTS = np.array([1.0, 2.0])

# Network A on TINY_INPUTS, on paper:
#   hidden sums  z = [1*0.5 + 2*0.25 + 0,  1*(-1) + 2*2 + 0.5] = [1.0, 3.5]
#   output sum   z = tanh(1.0)*1 + tanh(3.5)*(-0.5) + 0.25 = 0.5125052...
HIDDEN_SUMS_A = np.array([1.0, 3.5])
OUTPUT_SUM_A = 0.5125052071501655
OUTPUT_A = 0.47189483546154964  # tanh(OUTPUT_SUM_A)

# Network B on TINY_INPUTS, on paper:
#   hidden sums  z = [1*(-0.5) + 2*1 + 0,  1*1 + 2*0.25 - 0.5] = [1.5, 1.0]
#   output sum   z = tanh(1.5)*0.5 + tanh(1.0)*1 - 0.25 = 0.9641682...
OUTPUT_SUM_B = 0.9641682827781981
OUTPUT_B = 0.7461303770188783  # tanh(OUTPUT_SUM_B)


def hidden_layer_a() -> Layer:
    return Layer(np.array([[0.5, -1.0], [0.25, 2.0]]), np.array([0.0, 0.5]))


def output_layer_a() -> Layer:
    return Layer(np.array([[1.0], [-0.5]]), np.array([0.25]))


def network_a() -> NeuralNetwork:
    return NeuralNetwork([hidden_layer_a(), output_layer_a()])


def network_b() -> NeuralNetwork:
    hidden_layer = Layer(np.array([[-0.5, 1.0], [1.0, 0.25]]), np.array([0.0, -0.5]))
    output_layer = Layer(np.array([[0.5], [1.0]]), np.array([-0.25]))
    return NeuralNetwork([hidden_layer, output_layer])
