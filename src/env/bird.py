import pygame as pg
from .utils import load_img, Image, centralize_x, SCREEN_CENTER
from typing import Literal


class Bird:

    IMAGE = load_img(Image.BIRD, (80, 80))
    X: int = centralize_x(IMAGE, SCREEN_CENTER[0])[0]

    def __init__(self) -> None:
        
        self.y = SCREEN_CENTER[1]
        self.velocity_y = 0
        self.gravity = 0.5
        self.lift = -10

    def step(self, action: Literal[0, 1]) -> None:

        if action not in (0, 1):
            raise ValueError('Invalid action')
        
        if action == 1:
            self.velocity_y = self.lift

        self.velocity_y += self.gravity
        self.y += self.velocity_y

    def render(self, screen: pg.Surface) -> None:
        screen.blit(self.IMAGE, (self.X, self.y))
        