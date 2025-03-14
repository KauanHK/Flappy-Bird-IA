import pygame as pg
from .utils import load_img, Image


class Background:

    WIDTH: int = 800
    HEIGHT: int = 600
    SIZE: tuple[int, int] = (WIDTH, HEIGHT)
    IMAGE: pg.Surface = load_img(Image.BACKGROUND, SIZE)

    def __init__(self) -> None:

        self.x: int = 0

    def update(self) -> None:

        self.x -= 1
        if self.x < -Background.WIDTH:
            self.x = 0

    def render(self, screen: pg.Surface) -> None:

        screen.blit(Background.IMAGE, (self.x, 0))
        screen.blit(Background.IMAGE, (self.x + Background.WIDTH, 0))
