import pytest
from unittest.mock import Mock, patch
from ..conftest import MockMask

import pygame as pg
from src.env.pipe import Pipe, Pipes
from src.env.utils import SCREEN_WIDTH
from collections import deque


class TestPipe:

    @pytest.fixture(scope = 'class', autouse = True)
    def mock_surface(self):
        """Fixture para criar um mock de pg.Surface."""

        mock_surface = Mock(spec = pg.Surface)
        mock_surface.get_width.return_value = Pipe.WIDTH
        mock_surface.get_height.return_value = Pipe.HEIGHT

        with patch('src.env.pipe.load_img', return_value = mock_surface):
            yield mock_surface

    def test_init(self):
        """Testa a inicialização de um Pipe."""

        pipe = Pipe(x = 100, y_lower = 400)
        assert pipe.x == 100
        assert pipe.y_lower == 400
        assert pipe.y_upper == 400 - Pipe.GAP - Pipe.HEIGHT


    def test_get_image_upper(self, mock_surface):
        """Testa o método get_image_upper com lazy loading."""

        # Resetar _IMAGE_UPPER para None antes do teste
        Pipe._IMAGE_UPPER = None
        assert Pipe.get_image_upper() == mock_surface
        assert Pipe._IMAGE_UPPER == mock_surface

        # Chama novamente para verificar se retorna a mesma imagem
        assert Pipe.get_image_upper() == mock_surface


    def test_get_image_lower(self, mock_surface):
        """Testa o método get_image_lower com lazy loading."""

        with patch('pygame.transform.flip', return_value = mock_surface):

            Pipe._IMAGE_LOWER = None
            assert Pipe.get_image_lower() == mock_surface
            assert Pipe._IMAGE_LOWER == mock_surface
            assert Pipe.get_image_lower() == mock_surface


    def test_get_mask_upper(self, mock_surface):
        """Testa o método get_mask_upper com lazy loading."""

        Pipe._MASK_UPPER = None
        mask = Pipe.get_mask_upper()
        assert isinstance(mask, MockMask)
        assert Pipe._MASK_UPPER == mask
        assert Pipe.get_mask_upper() == mask


    def test_get_mask_lower(self, mock_surface):
        """Testa o método get_mask_lower com lazy loading."""

        with patch('pygame.transform.flip', return_value=mock_surface):

            Pipe._MASK_LOWER = None
            mask = Pipe.get_mask_lower()
            assert isinstance(mask, MockMask)
            assert Pipe._MASK_LOWER == mask
            assert Pipe.get_mask_lower() == mask


    def test_new_pipe(self, ):
        """Testa a criação de um Pipe com y aleatório."""

        with patch('src.env.pipe.Pipe.random_y', return_value=300):
            pipe = Pipe.new_pipe(x = 200)
            assert pipe.x == 200
            assert pipe.y_lower == 300


    def test_random_y(self, ):
        """Testa se random_y retorna um valor entre MIN_Y e MAX_Y."""

        y = Pipe.random_y()
        assert Pipe.MIN_Y <= y <= Pipe.MAX_Y


    def test_update(self, ):
        """Testa a atualização da posição do Pipe."""

        x = 100
        pipe = Pipe(x = x, y_lower = 400)
        pipe.update()
        assert pipe.x == x + Pipe.VELOCITY_X


    def test_render(self, mock_surface):
        """Testa o método render."""

        screen = Mock(spec = pg.Surface)
        pipe = Pipe(x = 100, y_lower = 400)
        
        with (
            patch('src.env.pipe.Pipe.get_image_upper', return_value=mock_surface),
            patch('src.env.pipe.Pipe.get_image_lower', return_value=mock_surface)
        ):
            pipe.render(screen)
            screen.blit.assert_any_call(mock_surface, (pipe.x, pipe.y_upper))
            screen.blit.assert_any_call(mock_surface, (pipe.x, pipe.y_lower))


class TestPipes:

    def test_init(self):
        """Testa a inicialização dos Pipes."""
        
        distance = 200
        pipes = Pipes(x_start = SCREEN_WIDTH, distance = distance)
        assert pipes.distance == distance
        assert isinstance(pipes.pipes, deque)

        # Verificar se existe exatamente um cano criado
        # porque x_start = SCREEN_WIDTH e os canos são criados enquanto x <= SCREEN_WIDTH
        assert len(pipes.pipes) == 1
        assert pipes.pipes[0].x == SCREEN_WIDTH

        # Canos iniciando no meio da tela com distância de um décimo da tela
        pipes = Pipes(x_start = SCREEN_WIDTH // 2, distance = SCREEN_WIDTH // 10)

        # Nesse caso, seis canos devem ter sido criados
        assert len(pipes) == 3
        x = SCREEN_WIDTH // 2
        for pipe in pipes:
            assert pipe.x == x
            x += Pipe.WIDTH + SCREEN_WIDTH // 10

    def test_update_no_pop(self):
        """Testa o método update sem remover canos."""

        pipes = Pipes()
        initial_len = len(pipes.pipes)
        lefts = [pipe.x for pipe in pipes.pipes]

        pipes.update()
        assert len(pipes) == initial_len
        for pipe, x in zip(pipes, lefts):
            assert pipe.x == x - 3

    def test_update_pop_and_append(self):
        """Testa o método update com remoção e adição de canos."""

        pipes = Pipes(x_start=400, distance=200)

        initial_len = len(pipes)
        first_pipe = pipes.pipes[0]
        first_pipe.x = -Pipe.WIDTH * 2
        pipes.update()
        assert first_pipe not in pipes
        assert len(pipes) == initial_len - 1

        initial_len = len(pipes)
        last_pipe = pipes[-1]
        last_pipe.x = SCREEN_WIDTH - Pipe.WIDTH - pipes.distance - 1
        pipes.update()
        assert last_pipe in pipes
        assert len(pipes) == initial_len + 1

    def test_render(self):
        """Testa o método render."""

        screen = Mock(spec=pg.Surface)
        pipes = Pipes(x_start=400, distance=200)
        with patch.object(Pipe, 'render') as mock_render:
            pipes.render(screen)
            assert mock_render.call_count == len(pipes.pipes)
            for pipe in pipes.pipes:
                mock_render.assert_any_call(screen)

    def test_get_next_pipes(self):
        """Testa o método get_next_pipes."""

        pipes = Pipes(x_start=400, distance=200)
        pipe1, pipe2 = pipes.get_next_pipes(x=300)
        assert pipe1 == pipes.pipes[0]
        assert pipe2 == pipes.pipes[1]

        # Testa quando x está depois do último pipe
        with pytest.raises(ValueError):
            pipes.get_next_pipes(x=1000)

        # Testa o último pipe
        pipe1, pipe2 = pipes.get_next_pipes(x=pipes.pipes[-1].x)
        assert pipe1 is pipe2

    def test_getitem(self):
        """Testa o método __getitem__."""

        pipes = Pipes(x_start = 400, distance = 200)
        assert pipes[0] == pipes.pipes[0]
        assert pipes[-1] == pipes.pipes[-1]
        with pytest.raises(IndexError):
            pipes[len(pipes.pipes)]  # Índice fora do alcance

    def test_iter(self):
        """Testa o método __iter__."""
        
        pipes = Pipes(x_start = 400, distance = 200)
        iterated_pipes = list(iter(pipes))
        assert len(iterated_pipes) == len(pipes.pipes)
        assert all(p1 == p2 for p1, p2 in zip(iterated_pipes, pipes.pipes))

    def test_len(self):
        """Testa o método __len__."""

        pipes = Pipes()
        assert len(pipes) == len(pipes.pipes)
