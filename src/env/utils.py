import pygame as pg
from pathlib import Path
from typing import NamedTuple


IMAGES_PATH = Path(__file__).parent.parent.parent / 'assets' / 'images'
print(IMAGES_PATH)

SCREEN_SIZE = (800, 600)
SCREEN_WIDTH = SCREEN_SIZE[0]
SCREEN_HEIGHT = SCREEN_SIZE[1]
SCREEN_CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
SCREEN_RECT = pg.Rect((0, 0), SCREEN_SIZE)


class Image:

    BIRD: str = IMAGES_PATH / 'bird.png'
    PIPE: str = IMAGES_PATH / 'pipe.png'
    BACKGROUND: str = IMAGES_PATH / 'background.jpg'


def load_img(image: str, size: tuple[int, int] | None = None) -> pg.Surface:
    
    image = pg.image.load(image).convert_alpha()
    if size is not None:
        image = pg.transform.scale(image, size)
    return image


def centralize(image: pg.Surface, center: tuple[int, int]) -> tuple[int, int]:
    return image.get_rect(center=center).topleft


def centralize_x(image: pg.Surface, centerx: int) -> tuple[int, int]:
    return image.get_rect(centerx = centerx).topleft


def centralize_y(image: pg.Surface, centery: int) -> tuple[int, int]:
    return image.get_rect(centery = centery).topleft
