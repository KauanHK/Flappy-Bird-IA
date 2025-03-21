import pytest
from unittest.mock import patch
import pygame as pg


@pytest.fixture
def setup_bird():
    with (
        patch('pygame.mask.from_surface', return_value = pg.mask.Mask((80, 80))),
        patch('pygame.mask.Mask.overlap', return_value = None)):
        yield
