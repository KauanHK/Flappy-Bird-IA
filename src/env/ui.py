import pygame as pg
from .bird import Bird
from .pipe import Pipes
from .background import Background
from .utils import SCREEN_SIZE, centralize_x, SCREEN_CENTER_X
from typing import Literal


class FlappyBirdUI:

    def __init__(self) -> None:

        pg.init()

        self.background = Background()
        self._font = pg.font.SysFont('Arial', 48)
        self._surface_score = self._create_surface_score(0)
        self._surface_birds_alive = self._create_surface_birds_alive([])
        self._screen = pg.display.set_mode(SCREEN_SIZE)
        self._clock = pg.time.Clock()

    def reset(self) -> None:

        self.background.reset()
        self._surface_score = self._create_surface_score(0)
        self._surface_birds_alive = self._create_surface_birds_alive([])

    def update(self, birds_alive: int, score: int | None = None) -> None:
        """Executa uma etapa no ambiente retorna o estado do jogo.

        :param score: Pontuação do jogo.
        :param birds_alive: Número de pássaros vivos.
        """

        self.background.update()
        if score is not None:
            self._surface_score = self._create_surface_score(score)
        self._surface_birds_alive = self._create_surface_birds_alive(birds_alive)

    def render(self, birds: list[Bird], pipes: Pipes) -> None:
        """Renderiza o ambiente. Se o ambiente não
        estiver configurado para renderizar, lançará uma exceção."""

        self._screen.fill((0, 0, 0))
        self.background.render(self._screen)

        pipes.render(self._screen)
        for bird in birds:
            bird.render(self._screen)

        self._screen.blit(self._surface_score, (centralize_x(self._surface_score, SCREEN_CENTER_X)[0], 20))
        self._screen.blit(self._surface_birds_alive, (centralize_x(self._surface_birds_alive, SCREEN_CENTER_X)[0], 60))

        self._clock.tick(60)
        pg.display.flip()

    def close(self) -> None:
        pg.quit()

    def _create_surface_score(self, score: int) -> pg.Surface:
        """Atualiza o score."""
        return self._font.render(str(score), True, (255, 255, 255))
    
    def _create_surface_birds_alive(self, birds_alive: int) -> pg.Surface:
        """Atualiza o Surface do número de pássaros vivos."""
        return self._font.render(str(birds_alive), True, (255, 255, 255))

    def __repr__(self) -> str:
        return f'FlappyBirdUI()'
