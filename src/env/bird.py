import pygame as pg
from .pipe import Pipe
from .utils import load_img, Image, centralize_x, SCREEN_CENTER_X, SCREEN_CENTER_Y, SCREEN_HEIGHT
from typing import Literal


class Bird:

    WIDTH: int = 80
    HEIGHT: int = 80
    SIZE: tuple[int, int] = (WIDTH, HEIGHT)

    IMAGE: pg.Surface = load_img(Image.BIRD, SIZE)
    MASK: pg.Mask = pg.mask.from_surface(IMAGE)

    X: int = centralize_x(IMAGE, SCREEN_CENTER_X)[0]
    GRAVITY: float = 0.5
    LIFT: int = -10
    FLOOR: int = SCREEN_HEIGHT - HEIGHT

    def __init__(self, y: int = SCREEN_CENTER_Y) -> None:
        """Inicializa um pássaro.

        :param y: Posição y do pássaro, padrão centery da tela.
        :param gravity: Valor da gravidade.
        :param lift: Potência de pulo.
        """
        
        self.y: int = y
        self.velocity_y: int = 0
        self.score: int = 0
        self.is_dead: bool = False

    def update(self, action: bool | Literal[0, 1], next_pipe: Pipe) -> None:
        """Atualiza um pássaro.

        :param action: 1 para pular, ou 0.
        :param next_pipe: O cano à sua frente.
        """

        if self.is_dead:
            return

        if not isinstance(action, bool) or action not in (0, 1):
            raise ValueError('A ação deve ser um booleano, 0 ou 1.')
        
        if action:
            self.velocity_y = Bird.LIFT

        self.velocity_y += Bird.GRAVITY
        self.y += self.velocity_y

        if self._collided(next_pipe):
            self.is_dead = True

    def render(self, screen: pg.Surface) -> None:
        """Renderiza o pássaro em screen."""
        screen.blit(Bird.IMAGE, (Bird.X, self.y))

    def _collided(self, pipe: Pipe) -> bool:
        """Retorna True se o colidiu com pipe, senão False."""

        offset_x = pipe.x - self.X
        offset_upper = (offset_x, pipe.y_upper - self.y)
        offset_lower = (offset_x, pipe.y_lower - self.y)
        return self.y < -Bird.HEIGHT//2 or self.y > Bird.FLOOR or Bird.MASK.overlap(pipe.MASK_UPPER, offset_upper) or Bird.MASK.overlap(pipe.MASK_LOWER, offset_lower)

    def __repr__(self) -> str:
        return f'Bird(y={self.y}, score={self.score}, is_dead={self.is_dead})'
        