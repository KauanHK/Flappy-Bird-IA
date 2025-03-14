import numpy as np
from numpy.typing import NDArray


def sigmoid(x: NDArray) -> NDArray:
    return 1 / (1 + np.exp(-x))


class NeuralNetwork:

    def __init__(self, weights: list[NDArray] | None = None, bias: list[NDArray] | None = None) -> None:
        """Rede neural para o jogo Flappy Bird."""

        if weights is not None:
            self.weights = weights
            self.bias = bias
            return

        self.weights = [
            np.random.uniform(-0.5, 0.5, (16, 2)),
            np.random.uniform(-0.5, 0.5, (1, 16))
        ]
        self.bias = [
            np.random.uniform(-0.5, 0.5, (16, 1)),
            np.random.uniform(-0.5, 0.5, (1, 1))
        ]

    def predict(self, a: NDArray) -> bool:

        for weights, bias in zip(self.weights, self.bias):
            a = sigmoid(weights @ a + bias)
        return a.argmax() > 0.5
