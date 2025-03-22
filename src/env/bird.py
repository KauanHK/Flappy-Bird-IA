import pygame as pg
from .pipe import Pipe
from .utils import load_img, Image, centralize_x, SCREEN_CENTER_X, SCREEN_CENTER_Y, SCREEN_HEIGHT
from typing import Literal


class DeadBirdError(BaseException): ...


class Bird:

    WIDTH: int = 80
    HEIGHT: int = 80
    SIZE: tuple[int, int] = (WIDTH, HEIGHT)

    _IMAGE: pg.Surface | None = None
    _MASK: pg.Mask | None = None

    X: int = SCREEN_CENTER_X - WIDTH // 2
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

    @classmethod
    def get_image(cls) -> pg.Surface:
        if cls._IMAGE is None:
            cls._IMAGE = load_img(Image.BIRD, cls.SIZE)
        return cls._IMAGE
    
    @classmethod
    def get_mask(cls) -> pg.Mask:
        if cls._MASK is None:
            cls._MASK = pg.mask.from_surface(cls.get_image())
        return cls._MASK

    def update(self, action: bool | Literal[0, 1], next_pipe: Pipe, scored: bool) -> None:
        """Atualiza um pássaro.

        :param action: 1 para pular, ou 0.
        :param next_pipe: O cano à sua frente.
        """

        if not self.is_alive:
            raise DeadBirdError('Não pode atualizar um pássaro que já morreu')

        if not isinstance(action, bool) and action not in (0, 1):
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
        screen.blit(Bird.get_image(), (Bird.X, self.y))

    def _collided(self, pipe: Pipe) -> bool:
        """Retorna True se o colidiu com pipe, senão False."""

        if self.y < -Bird.HEIGHT//2 or self.y > Bird.FLOOR:
            return True

        offset_x = pipe.x - Bird.X
        if offset_x > Bird.WIDTH:
            return False

        offset_upper = (offset_x, pipe.y_upper - self.y)
        offset_lower = (offset_x, pipe.y_lower - self.y)
        return Bird.get_mask().overlap(pipe.get_mask_upper(), offset_upper) is not None\
                or Bird.get_mask().overlap(pipe.get_mask_lower(), offset_lower) is not None

    def __repr__(self) -> str:
        return f'Bird(y={self.y}, velocity_y={self.velocity_y}, steps={self.steps}, is_alive={self.is_alive})'
        