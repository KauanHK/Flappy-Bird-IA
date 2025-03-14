import pygame as pg
from .bird import Bird
from .pipe import Pipes, Pipe
from .utils import SCREEN_SIZE
import math
from typing import NamedTuple, Literal


class EnvClosedError(BaseException): ...


class State(NamedTuple):
    """Estados do ambiente."""

    distance_upper: float
    distance_lower: float
    done: bool


class FlappyBird:

    def __init__(self, birds: int, gui: bool = False) -> None:

        self.birds: list[Bird] = [Bird() for _ in range(birds)]
        self.pipes = Pipes()
        self.done: bool = False
        self.next_pipe: Pipe = self.pipes.get_next_pipe(Bird.X)

        self.gui: bool = gui
        if self.gui:
            from .background import Background
            self.background: Background = Background()
            pg.init()
            self._screen = pg.display.set_mode(SCREEN_SIZE)
            self._clock = pg.time.Clock()

    def step(self, actions: list[Literal[0, 1] | bool]) -> State:
        """Executa uma etapa no ambiente retorna o estado do jogo.

        :param actions: lista com as ações de cada pássaro.
        """

        self._check_is_not_closed()

        if self.gui:
            self.background.update()
        self.pipes.update()
        next_pipe = self.pipes.get_next_pipe(Bird.X)
        scored = self.next_pipe != next_pipe
        self.next_pipe = next_pipe
        for bird, action in zip(self.birds, actions):
            bird.update(bool(action), next_pipe)
            bird.score += scored

        birds_alive = list(filter(lambda b: not b.is_dead, self.birds))
        if not birds_alive:
            distance_upper = 0
            distance_lower = 0
            self.done = True
        else:
            bird = birds_alive[0]
            right = Bird.X + Bird.WIDTH
            middle_right = bird.y + Bird.HEIGHT//2

            square_distance_x = (next_pipe.x - right) ** 2
            distance_upper = math.sqrt(square_distance_x + (next_pipe.y_upper-Pipe.HEIGHT - middle_right) ** 2)
            distance_lower = math.sqrt(square_distance_x + (next_pipe.y_lower - middle_right) ** 2)

        return State(distance_upper, distance_lower, self.done)

    def render(self) -> None:
        """Renderiza o ambiente. Se o ambiente não
        estiver configurado para renderizar, lançará uma exceção."""

        self._check_is_not_closed()
        self._screen.fill((0, 0, 0))

        if self.gui:
            self.background.render(self._screen)
        for bird in self.birds:
            bird.render(self._screen)
        self.pipes.render(self._screen)

        self._clock.tick(60)
        pg.display.flip()

    def close(self) -> None:
        """Fecha o ambiente. Se já estiver fechado, não tem efeito algum."""
        self.done = True
        pg.quit()

    def _check_is_not_closed(self) -> None:
        """Verifica se o ambiente está em funcionamento.
        Se estiver fechado, lança uma exceção EnvClosedError,
        senão retorna None."""

        if self.done:
            raise EnvClosedError('Ambiente já fechado.')
