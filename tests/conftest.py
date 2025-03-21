import pytest
from unittest.mock import patch
from typing import Self


class MockMask:
    _collides: bool = False

    def __init__(self, size: tuple[int, int], fill: bool = False) -> None:

        if (
                not isinstance(size, tuple) or
                len(size) != 2 or
                not (all(isinstance(n, int) for n in size))
        ):
            raise TypeError(f"Parâmetro 'size' deve ser uma tupla de dois int's, não {type(size).__name__}")
        if not isinstance(fill, bool):
            raise TypeError(f"Parâmetro 'fill' deve ser do tipo bool, não {type(fill).__name__}")

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
    with patch('pygame.mask.from_surface', return_value = lambda *args, **kwargs: MockMask(*args, **kwargs)):
        yield


@pytest.fixture
def default_bird(setup):
    from src.env import Bird
    return Bird()
