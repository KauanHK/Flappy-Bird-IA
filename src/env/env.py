import pygame as pg
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
        self.pipes = Pipes()

        self.steps = 0
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

        self.ui.reset()

        return self.get_states()

    def step(self, actions: list[Literal[0, 1] | bool]) -> tuple[list[NDArray], bool]:
        """Executa uma etapa no ambiente retorna o estado do jogo.

        :param actions: lista com as ações de cada pássaro.
        """

        self._check_is_not_closed()

        self.pipes.update()

        next_pipe = self.pipes.get_next_pipes(Bird.X)
        scored = self._next_pipes[0] != next_pipe[0]
        self._next_pipes = next_pipe

        for bird, action in zip(self.birds, actions):
            if bird.is_alive:
                bird.update(bool(action), next_pipe[0])

        self.ui.update(self.birds, scored)
        self.steps += 1
        return self.get_states(), list(map(lambda bird: not bird.is_alive, self.birds))

    def get_states(self) -> list[NDArray]:

        states: list[NDArray] = []
        for bird in self.birds:

            states.append(np.array([
                (self._next_pipes[0].x - bird.X + Bird.WIDTH) / SCREEN_WIDTH,
                (self._next_pipes[0].y_upper + Pipe.HEIGHT - bird.y) / SCREEN_HEIGHT,
                (self._next_pipes[0].y_lower - bird.y) / SCREEN_HEIGHT,
                bird.velocity_y / SCREEN_HEIGHT,
                ])
            )

        return states

    def render(self) -> None:
        """Renderiza o ambiente. Se o ambiente não
        estiver configurado para renderizar, lançará uma exceção."""

        self.ui.render(self.birds, self.pipes)

    def close(self) -> None:
        """Fecha o ambiente. Se já estiver fechado, não tem efeito algum."""
        
        for bird in self.birds:
            bird.kill()
        pg.quit()

    def _check_is_not_closed(self) -> None:
        """Verifica se o ambiente está em funcionamento.
        Se estiver fechado, lança uma exceção EnvClosedError,
        senão retorna None."""

        if self.done:
            raise EnvClosedError('Ambiente já fechado.')

    def __repr__(self) -> str:
        return f'FlappyBird(birds_alive={len(self.birds)}, score={self.score})'
