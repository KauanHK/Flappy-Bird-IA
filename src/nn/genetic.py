import numpy as np
import random
from .nn import NeuralNetwork


def crossover(nn1: NeuralNetwork, nn2: NeuralNetwork) -> NeuralNetwork:

    child_weights = []
    child_bias = []
    for w1, b1, w2, b2 in zip(nn1.weights, nn1.bias, nn2.weights, nn2.bias):

        # Cruzamento dos pesos
        mask = np.random.random(w1.shape) < 0.5
        child_weights.append(np.where(mask, w1, w2))

        # Cruzamento dos bias
        mask = np.random.random(b1.shape) < 0.5
        child_bias.append(np.where(mask, b1, b2))

    return NeuralNetwork(child_weights, child_bias)


def mutate(nn: NeuralNetwork, rate: float = 0.05, strength: float = 0.1) -> None:

    if random.random() > rate:
        return

    for weights, bias in zip(nn.weights, nn.bias):

        # Máscara para indicar quais pesos sofrerão mutação
        mask = np.random.random(weights.shape) < rate

        # Mutações para cada peso
        mutations = np.random.normal(0, strength, weights.shape)
        weights[mask] += mutations[mask]

        # Mutações para cada bias
        mask = np.random.random(bias.shape) < rate
        mutations = np.random.normal(0, strength, bias.shape)
        bias[mask] += mutations[mask]
