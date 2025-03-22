import pytest

from ..conftest import MockMask

from src.env import Bird, Pipe


@pytest.mark.parametrize(
    ('size', 'fill'),
    (
        (('a', 'b'), True),
        ((10, 10), 'a'),
        ('a', '')
    )
)
def test_invalid_params_mock_mask(size, fill):
    with pytest.raises(TypeError):
        MockMask(size, fill)


def test_mocks():
    
    assert isinstance(Bird.get_mask(), MockMask)
    assert isinstance(Pipe.get_mask_upper(), MockMask)
    assert isinstance(Pipe.get_mask_lower(), MockMask)
