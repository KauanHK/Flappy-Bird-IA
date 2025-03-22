import pytest
from unittest.mock import patch

import pygame as pg
from typing import Self


class MockMask:
    _collides: bool = False

    def __init__(self, surface: pg.Surface, threshold: int = 127) -> None:

        if not isinstance(surface, pg.Surface):
            raise TypeError(f"Parâmetro 'surface' deve ser do tipo pygame.Surface, não {type(surface).__name__}")
        if not isinstance(threshold, int):
            raise TypeError(f"Parâmetro 'threshold' deve ser do tipo int, não {type(threshold).__name__}")

    def overlap(self, other: Self, offset: tuple[int, int]) -> tuple[int, int] | None:

        if not isinstance(other, MockMask):
            raise TypeError(f"Parâmetro 'other' deve ser do tipo MockMask, não {type(other).__name__}")
        elif not isinstance(offset, tuple) or len(offset) != 2:
            raise TypeError(f"Parâmetro 'offset' deve ser uma tupla de dois int's, não {type(offset).__name__}")

        return (0, 0) if self._collides else None

    @classmethod
    def set_overlap_return_value(cls, collides: bool) -> None:
        cls._collides = collides


@pytest.fixture(scope = 'session', autouse = True)
def setup():
    with patch('pygame.mask.from_surface') as mock:
        mock.side_effect = lambda *args, **kwargs: MockMask(*args, **kwargs)
        yield


@pytest.fixture
def default_bird():
    from src.env import Bird
    return Bird()
