import pygame as pg
import numpy as np
from numpy.typing import NDArray
from .bird import Bird
from .pipe import Pipes, Pipe
from .utils import SCREEN_SIZE, SCREEN_CENTER_X, centralize_x
from typing import Literal


class EnvClosedError(BaseException): ...


class FlappyBird:

    def __init__(self, num_birds: int, gui: bool = False) -> None:

        self.num_birds: int = num_birds
        self.birds: list[Bird] = [Bird() for _ in range(num_birds)]
        self.pipes = Pipes()
        self.done: bool = False
        self.next_pipe: Pipe = self.pipes.get_next_pipe(Bird.X)

        self.steps = 0
        self.frames_alive = [0]*self.num_birds

        self.gui: bool = gui
        if self.gui:
            pg.init()
            from .background import Background
            self.background = Background()
            self.score = 0
            self._font = pg.font.SysFont('Arial', 48)
            self._surface_score = self._create_surface_score()
            self._screen = pg.display.set_mode(SCREEN_SIZE)
            self._clock = pg.time.Clock()

    def reset(self) -> list[NDArray]:
        """Reinicia o ambiente."""

        self.birds: list[Bird] = [Bird() for _ in range(self.num_birds)]
        self.pipes = Pipes()
        self.done: bool = False
        self.next_pipe: Pipe = self.pipes.get_next_pipe(Bird.X)

        self.steps = 0
        self.frames_alive = [0] * self.num_birds

        if self.gui:
            from .background import Background
            self.background = Background()
            self.score = 0
            self._surface_score = self._create_surface_score()

        return self.get_states()

    def step(self, actions: list[Literal[0, 1] | bool]) -> list[NDArray]:
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

        if scored:
            self.score += 1
            self._surface_score = self._create_surface_score()

        i = 0
        for bird, action in zip(self.birds, actions):

            if bird.is_dead:
                continue
            bird.update(bool(action), next_pipe)
            if bird.is_dead:
                self.frames_alive[i] = self.steps
            else:
                bird.score += scored
            i += 1

        self.steps += 1

        return self.get_states()

    def get_states(self) -> list[NDArray]:

        states: list[NDArray] = []
        for bird in self.birds:

            states.append(np.array([
                self.next_pipe.x - bird.X,
                self.next_pipe.y_upper + Pipe.HEIGHT - bird.y,
                self.next_pipe.y_lower - bird.y,
                bird.velocity_y,
                ])
            )

        birds_alive = list(filter(lambda b: not b.is_dead, self.birds))
        self.done = not birds_alive

        return states

    def render(self) -> None:
        """Renderiza o ambiente. Se o ambiente não
        estiver configurado para renderizar, lançará uma exceção."""

        self._screen.fill((0, 0, 0))

        if self.gui:
            self.background.render(self._screen)
        for bird in self.birds:
            if not bird.is_dead:
                bird.render(self._screen)
        self.pipes.render(self._screen)
        self._screen.blit(self._surface_score, (centralize_x(self._surface_score, SCREEN_CENTER_X)[0], 20))

        self._clock.tick(60)
        pg.display.flip()

    def close(self) -> None:
        """Fecha o ambiente. Se já estiver fechado, não tem efeito algum."""
        self.done = True
        pg.quit()

    def _create_surface_score(self) -> pg.Surface:
        """Atualiza o score."""
        return self._font.render(str(self.score), True, (255, 255, 255))

    def _check_is_not_closed(self) -> None:
        """Verifica se o ambiente está em funcionamento.
        Se estiver fechado, lança uma exceção EnvClosedError,
        senão retorna None."""

        if self.done:
            raise EnvClosedError('Ambiente já fechado.')

    def __repr__(self) -> str:
        return f'FlappyBird(birds_alive={len(self.birds)}, score={self.score})'
