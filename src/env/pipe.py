import pygame as pg
from .utils import SCREEN_HEIGHT, load_img, Image, SCREEN_WIDTH
import random
from collections import deque
from typing import Self, Iterator


class Pipe:

    WIDTH: int = 80
    HEIGHT: int = SCREEN_HEIGHT
    SIZE: tuple[int, int] = (WIDTH, HEIGHT)

    IMAGE_UPPER: pg.Surface = load_img(Image.PIPE, SIZE)
    IMAGE_LOWER: pg.Surface = pg.transform.flip(IMAGE_UPPER, False, True)

    MASK_UPPER: pg.Mask = pg.mask.from_surface(IMAGE_UPPER)
    MASK_LOWER: pg.Mask = pg.mask.from_surface(IMAGE_LOWER)

    GAP: int = 150
    MIN_Y: int = GAP
    MAX_Y: int = SCREEN_HEIGHT - GAP

    def __init__(self, x: int, y_lower: int) -> None:
        """Inicializa um cano.

        :param x: Posição x do cano
        :param y_lower: Posição y do cano inferior.
        """

        self.x: int = x
        self.y_lower: int = y_lower
        self.y_upper: int = y_lower - Pipe.GAP - Pipe.IMAGE_UPPER.get_height()
        self.velocity_x: int = -3

    @classmethod
    def new_pipe(cls, x: int) -> Self:
        """Retorna um Pipe com um y aleatório.

        :param x: Posição x do cano.
        """
        return cls(x, cls.random_y())

    @classmethod
    def random_y(cls) -> int:
        """Retorna um y aleatório entre MIN_Y E MAX_Y."""
        return random.randint(cls.MIN_Y, cls.MAX_Y)

    def update(self) -> None:
        """Atualiza o cano."""
        self.x += self.velocity_x

    def render(self, screen: pg.Surface) -> None:
        """Renderiza o cano em screen."""
        screen.blit(self.IMAGE_UPPER, (self.x, self.y_upper))
        screen.blit(self.IMAGE_LOWER, (self.x, self.y_lower))

    def __repr__(self) -> str:
        return f'Pipe(x={self.x}, y_lower={self.y_lower}, y_upper={self.y_upper})'


class Pipes:

    def __init__(self, x_start: int = SCREEN_WIDTH, distance: int = 200) -> None:
        """Inicializa os canos."""

        self.distance: int = distance
        self.pipes: deque[Pipe] = self._create_pipes(x_start)

    def update(self) -> None:
        """Atualiza os canos."""

        for pipe in self.pipes:
            pipe.update()

        if self.pipes[0].x < - Pipe.WIDTH:
            self.pipes.popleft()
        if self.pipes[-1].x + Pipe.WIDTH < SCREEN_WIDTH - self.distance:
            self.pipes.append(Pipe.new_pipe(self.pipes[-1].x + Pipe.WIDTH + self.distance))

    def render(self, screen: pg.Surface) -> None:
        """Renderiza os canos em screen."""
        for pipe in self.pipes:
            pipe.render(screen)

    def get_next_pipes(self, x: int) -> tuple[Pipe, Pipe]:
        """Retorna o cano mais próximo de `x`,
        considerando apenas os canos à sua frente,
        ou seja, o cano com o menor x entre os canos com x > `x`.
        """

        for i, pipe in enumerate(self.pipes):
            if pipe.x + Pipe.WIDTH > x:
                if i == len(self.pipes) - 1:
                    return pipe, pipe
                return pipe, self.pipes[i+1]

        raise ValueError(f'Valor de x inválido ({x})')

    def _create_pipes(self, x_start: int) -> deque[Pipe]:
        """Cria os canos, com o x começando em x_start."""

        x = x_start
        pipes = deque()
        while x <= SCREEN_WIDTH:
            pipes.append(Pipe.new_pipe(x))
            x += Pipe.WIDTH + self.distance
        return pipes

    def __getitem__(self, index: int) -> Pipe:
        return self.pipes[index]

    def __iter__(self) -> Iterator[Pipe]:
        return iter(self.pipes)

    def __len__(self) -> int:
        return len(self.pipes)

    def __repr__(self) -> str:
        return f'Pipes({self.pipes})'
