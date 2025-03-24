import pytest
from unittest.mock import Mock, patch

import numpy as np
from src.env.env import FlappyBird, EnvClosedError
from src.env import Bird
from src.env.ui import FlappyBirdUI
from src.env.utils import SCREEN_WIDTH, SCREEN_HEIGHT


class TestFlappyBird:

    @pytest.fixture(scope = 'class', autouse = True)
    def setup_class(self):
        with patch('src.env.env.FlappyBirdUI', Mock(spec = FlappyBirdUI)):
            yield

    def test_init(self):
        """Testa a inicialização com GUI."""

        num_birds = 2
        env = FlappyBird(num_birds = num_birds, gui = True)
        assert env.num_birds == num_birds
        assert len(env.birds) == num_birds
        assert hasattr(env, 'ui')
        assert isinstance(env.ui, Mock)

    def test_birds_alive(self):
        """Testa a propriedade birds_alive."""

        env = FlappyBird(num_birds=3, gui=False)
        assert len(env.birds_alive) == 3
        env.birds[0].kill()
        assert len(env.birds_alive) == 2

    def test_done(self):
        """Testa a propriedade done."""

        env = FlappyBird(num_birds=2, gui=False)
        assert env.done is False
        for bird in env.birds:
            bird.kill()
        assert env.done is True

    def test_reset(self):
        """Testa o método reset."""

        env = FlappyBird(num_birds=2, gui=True)
        env.score = 10
        env.steps = 5
        env.birds[0].kill()
        states = env.reset()
        assert len(env.birds) == 2
        assert all(bird.is_alive for bird in env.birds)
        assert env.score == 0
        assert env.steps == 0
        assert len(states) == 2
        assert isinstance(states[0], np.ndarray)
        env.ui.reset.assert_called_once()

    def test_step_valid(self):
        """Testa o método step com ações válidas."""

        env = FlappyBird(num_birds = 2, gui = True)

        actions = [True, False]
        states = env.step(actions)

        assert env.steps == 1
        assert len(states) == 2
        assert isinstance(states[0], np.ndarray)
        assert env.birds[0].velocity_y == Bird.LIFT

        env.ui.update.assert_called_once_with(2, env.score)

    def test_step_invalid_actions(self):
        """Testa o método step com número errado de ações."""

        env = FlappyBird(num_birds=2, gui=False)
        with pytest.raises(ValueError, match='O número de ações deve ser igual ao número de pássaros'):
            env.step([True])  # Apenas uma ação para dois pássaros

    def test_step_score(self):
        """Testa o incremento do score em step."""

        env = FlappyBird(num_birds=1, gui=False)
        env.pipes.pipes[0].x = 40  # Simula o pipe passando o pássaro
        env.step([False])
        assert env.score == 1  # Score deve aumentar quando o pipe é passado

    def test_get_states(self):
        """Testa o método get_states."""
        
        env = FlappyBird(num_birds = 2, gui = False)
        
        states = env.get_states()
        assert len(states) == 2

        state = states[0]
        assert state.shape == (4,)
        x = env._next_pipes[0].x

        assert state[0] == max((x - (Bird.X + Bird.WIDTH)) / SCREEN_WIDTH, 0) 
        assert isinstance(state[1], float)
        assert isinstance(state[2], float)
        assert state[3] == 0 / SCREEN_HEIGHT

    def test_render(self):
        """Testa o método render com GUI."""

        env = FlappyBird(num_birds=1, gui=True)
        env.render()
        env.ui.render.assert_called_once_with(env.birds_alive, env.pipes)

    def test_render_no_gui(self):
        """Testa o método render sem GUI."""

        env = FlappyBird(num_birds=1, gui=False)
        with pytest.raises(AttributeError):
            env.render()

    def test_close(self):
        """Testa o método close."""

        env = FlappyBird(num_birds=2, gui=True)
        env.close()
        assert all(not bird.is_alive for bird in env.birds)
        env.ui.close.assert_called_once()

    def test_check_is_not_closed(self):
        """Testa o método _check_is_not_closed."""

        env = FlappyBird(num_birds=1, gui=False)
        env._check_is_not_closed()  # Não deve lançar exceção
        env.birds[0].kill()
        with pytest.raises(EnvClosedError, match='Ambiente já fechado'):
            env._check_is_not_closed()

    def test_repr(self):
        """Testa a representação em string."""

        env = FlappyBird(num_birds=3, gui=False)
        assert repr(env) == 'FlappyBird(birds_alive=3, score=0)'