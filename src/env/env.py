import numpy as np
from numpy.typing import NDArray
from .ui import FlappyBirdUI
from .bird import Bird
from .pipe import Pipes, Pipe
from .utils import SCREEN_WIDTH, SCREEN_HEIGHT
from typing import Literal


class EnvClosedError(BaseException): ...


class FlappyBird:

    def __init__(self, num_birds: int, gui: bool = False) -> None:

        self.num_birds: int = num_birds

        self.birds: list[Bird] = [Bird() for _ in range(num_birds)]
        self.pipes: Pipes = Pipes()

        self.score: int = 0
        self.steps: int = 0
        self._next_pipes: tuple[Pipe, Pipe] = self.pipes.get_next_pipes(Bird.X)

        if gui:
            self.ui: FlappyBirdUI = FlappyBirdUI()

    @property
    def birds_alive(self) -> list[Bird]:
        return list(filter(lambda b: b.is_alive, self.birds))

    @property
    def done(self) -> bool:
        return len(self.birds_alive) == 0
    
    def reset(self) -> list[NDArray]:
        """Reinicia o ambiente."""

        self.birds = [Bird() for _ in range(self.num_birds)]
        self.pipes = Pipes()

        self._next_pipes = self.pipes.get_next_pipes(Bird.X)
        self.steps = 0
        self.score = 0

        if hasattr(self, 'ui'):
            self.ui.reset()

        return self.get_states()

    def step(self, actions: list[Literal[0, 1] | bool]) -> list[NDArray]:
        """Executa uma etapa no ambiente retorna o estado do jogo.

        :param actions: lista com as ações de cada pássaro.
        """

        self._check_is_not_closed()
        if len(actions) != len(self.birds):
            raise ValueError(f'O número de ações deve ser igual ao número de pássaros. {len(actions)} != {len(self.birds)}')

        self.pipes.update()

        next_pipes = self.pipes.get_next_pipes(Bird.X)
        scored = self._next_pipes[0] != next_pipes[0]
        self._next_pipes = next_pipes

        self.score += scored
        self.steps += 1

        for bird, action in zip(self.birds, actions):
            if bird.is_alive:
                bird.update(bool(action), next_pipes[0], scored)

        if hasattr(self, 'ui'):
            self.ui.update(len(self.birds_alive), self.score)
        return self.get_states()

    def get_states(self) -> list[NDArray]:

        distance_x: float = (self._next_pipes[0].x - (Bird.X + Bird.WIDTH)) / SCREEN_WIDTH
        distance_x = max(distance_x, 0)
        y_upper: float = self._next_pipes[0].y_upper + Pipe.HEIGHT
        y_lower: float = self._next_pipes[0].y_lower

        states: list[NDArray] = []
        for bird in self.birds:
            bird_middle_right = bird.y + Bird.HEIGHT // 2
            states.append(np.array([
                distance_x,                                         # Distância horizontal para o próximo cano
                (y_upper - bird_middle_right) / SCREEN_HEIGHT,      # Distância vertical para a abertura de cima
                (y_lower - bird_middle_right) / SCREEN_HEIGHT,      # Distância vertical para a abertura de baixo
                bird.velocity_y / SCREEN_HEIGHT,                    # Velocidade vertical do pássaro
                ])
            )

        return states

    def render(self) -> None:
        """Renderiza o ambiente. Se o ambiente não
        estiver configurado para renderizar, lançará uma exceção."""

        self.ui.render(self.birds_alive, self.pipes)

    def close(self) -> None:
        """Fecha o ambiente. Se já estiver fechado, não tem efeito algum."""
        
        for bird in self.birds:
            bird.kill()
        if hasattr(self, 'ui'):
            self.ui.close()

    def _check_is_not_closed(self) -> None:
        """Verifica se o ambiente está em funcionamento.
        Se estiver fechado, lança uma exceção EnvClosedError,
        senão retorna None."""

        if not self.birds_alive:
            raise EnvClosedError('Ambiente já fechado.')

    def __repr__(self) -> str:
        return f'FlappyBird(birds_alive={len(self.birds)}, score={self.score})'
