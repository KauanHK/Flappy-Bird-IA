import pygame as pg
from .pipe import Pipe
from .utils import load_img, Image, centralize_x, SCREEN_CENTER_X, SCREEN_CENTER_Y, SCREEN_HEIGHT
from typing import Literal


class DeadBirdError(BaseException): ...

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
        self.steps: int = 0
        self.is_alive: bool = True
        self.score: int = 0

    def update(self, action: bool | Literal[0, 1], next_pipe: Pipe, scored: bool) -> None:
        """Atualiza um pássaro.

        :param action: 1 para pular, ou 0.
        :param next_pipe: O cano à sua frente.
        """

        if not self.is_alive:
            raise DeadBirdError('Não pode atualizar um pássaro que já morreu')

        if not isinstance(action, bool) or action not in (0, 1):
            raise ValueError('A ação deve ser um booleano, 0 ou 1.')
        
        if action:
            self.velocity_y = Bird.LIFT
        else:
            self.velocity_y += Bird.GRAVITY
        self.y += self.velocity_y

        if self._collided(next_pipe):
            self.is_alive = False
        else:
            self.steps += 1
            self.score += scored

    def kill(self) -> None:
        self.is_alive = False

    def render(self, screen: pg.Surface) -> None:
        """Renderiza o pássaro em screen."""
        screen.blit(Bird.IMAGE, (Bird.X, self.y))

    def _collided(self, pipe: Pipe) -> bool:
        """Retorna True se o colidiu com pipe, senão False."""

        if self.y < -Bird.HEIGHT//2 or self.y > Bird.FLOOR:
            return True

        offset_x = pipe.x - Bird.X
        if offset_x > Bird.WIDTH:
            return False

        offset_upper = (offset_x, pipe.y_upper - self.y)
        offset_lower = (offset_x, pipe.y_lower - self.y)
        return Bird.MASK.overlap(pipe.MASK_UPPER, offset_upper) is not None\
                or Bird.MASK.overlap(pipe.MASK_LOWER, offset_lower) is not None

    def __repr__(self) -> str:
        return f'Bird(y={self.y}, velocity_y={self.velocity_y}, steps={self.steps}, is_alive={self.is_alive})'
        