import numpy as np
from numpy.typing import NDArray


def ReLu(x: NDArray) -> NDArray:
    return np.maximum(0, x)


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
            np.random.uniform(-0.5, 0.5, (16, 4)),
            np.random.uniform(-0.5, 0.5, (2, 16))
        ]
        self.bias = [
            np.random.uniform(-0.5, 0.5, (16, 1)),
            np.random.uniform(-0.5, 0.5, (2, 1))
        ]

    def predict(self, a: NDArray) -> bool:

        for weights, bias in zip(self.weights[:-1], self.bias[:-1]):
            a = ReLu(weights @ a + bias)
        a = sigmoid(self.weights[-1] @ a + self.bias[-1])
        return a.argmax()
