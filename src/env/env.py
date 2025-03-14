import pygame as pg
from .bird import Bird
from .pipe import Pipes, Pipe
from .utils import SCREEN_SIZE, SCREEN_CENTER_X, centralize_x
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
            pg.init()
            from .background import Background
            self.background = Background()
            self.score = 0
            self._font = pg.font.SysFont('Arial', 48)
            self._surface_score = self._create_surface_score()
            self._screen = pg.display.set_mode(SCREEN_SIZE)
            self._clock = pg.time.Clock()

    def step(self, actions: list[Literal[0, 1] | bool]) -> list[State]:
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

        states: list[State] = []
        for bird, action in zip(self.birds, actions):

            bird.update(bool(action), next_pipe)
            if bird.is_dead:
                states.append(State(0, 0, True))
                continue
            bird.score += scored

            # A distância do pássaro para o cano do topo é
            # a distância entre o bottomleft do cano do topo e o topright do pássaro
            # A distância do pássaro para o cano de baixo é
            # a distância entre o topleft do cano de baixo e o bottomright do pássaro
            # Usa-se pitágoras para fazer esse cálculo
            # d^2 = dx^2 + dy^2
            # SE O PÁSSARO ESTIVER ENTRE OS CANOS, A DISTÂNCIA É APENAS A DIFERENÇA DO EIXO Y

            bird_right = Bird.X + Bird.WIDTH
            bird_top = bird.y
            bird_bottom = bird.y + Bird.HEIGHT

            pipe_left = next_pipe.x
            pipe_lower_top = next_pipe.y_lower
            pipe_upper_bottom = next_pipe.y_upper + Pipe.HEIGHT

            if bird_right >= next_pipe.x:
                states.append(State(bird_top - pipe_upper_bottom, pipe_lower_top - bird_bottom, True))
                continue

            states.append(State(
                math.sqrt((pipe_left - bird_top) ** 2 + (pipe_upper_bottom - bird_top) ** 2),
                math.sqrt((pipe_left - bird_right) ** 2 + (pipe_lower_top - bird_bottom) ** 2),
                False
            ))

        birds_alive = list(filter(lambda b: not b.is_dead, self.birds))
        self.done = not birds_alive

        return states

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
