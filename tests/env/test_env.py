import pytest
from unittest.mock import Mock, patch
import numpy as np
from src.env.env import FlappyBird, EnvClosedError


class MockPipes:

    def __init__(self):
        self.pipes = [MockPipe(x=300, y_lower=400)]

    def update(self):
        for pipe in self.pipes:
            pipe.update()

    def get_next_pipes(self, bird_x):
        return (self.pipes[0], None)  # Retorna apenas o próximo pipe


@pytest.fixture
def mock_env():
    """Fixture para configurar mocks globais."""
    with patch('flappybird.Bird', MockBird), \
         patch('flappybird.Pipes', MockPipes), \
         patch('flappybird.Pipe', MockPipe), \
         patch('flappybird.FlappyBirdUI', Mock):
        yield


class TestFlappyBird:

    def test_init_no_gui(self, mock_env):
        """Testa a inicialização sem GUI."""
        env = FlappyBird(num_birds=3, gui=False)
        assert env.num_birds == 3
        assert len(env.birds) == 3
        assert all(isinstance(bird, MockBird) for bird in env.birds)
        assert isinstance(env.pipes, MockPipes)
        assert env.score == 0
        assert env.steps == 0
        assert not hasattr(env, 'ui')

    def test_init_with_gui(self, mock_env):
        """Testa a inicialização com GUI."""
        env = FlappyBird(num_birds=2, gui=True)
        assert env.num_birds == 2
        assert len(env.birds) == 2
        assert hasattr(env, 'ui')
        assert isinstance(env.ui, Mock)

    def test_birds_alive(self, mock_env):
        """Testa a propriedade birds_alive."""
        env = FlappyBird(num_birds=3, gui=False)
        assert len(env.birds_alive) == 3
        env.birds[0].kill()
        assert len(env.birds_alive) == 2

    def test_done(self, mock_env):
        """Testa a propriedade done."""
        env = FlappyBird(num_birds=2, gui=False)
        assert env.done is False
        for bird in env.birds:
            bird.kill()
        assert env.done is True

    def test_reset(self, mock_env):
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

    def test_step_valid(self, mock_env):
        """Testa o método step com ações válidas."""
        env = FlappyBird(num_birds=2, gui=True)
        actions = [True, False]
        states = env.step(actions)
        assert env.steps == 1
        assert len(states) == 2
        assert isinstance(states[0], np.ndarray)
        assert env.birds[0].velocity_y == -5  # Pulo
        assert env.birds[1].velocity_y == 1   # Gravidade
        env.ui.update.assert_called_once_with(2, env.score)

    def test_step_invalid_actions(self, mock_env):
        """Testa o método step com número errado de ações."""
        env = FlappyBird(num_birds=2, gui=False)
        with pytest.raises(ValueError, match='O número de ações deve ser igual ao número de pássaros'):
            env.step([True])  # Apenas uma ação para dois pássaros

    def test_step_score(self, mock_env):
        """Testa o incremento do score em step."""
        env = FlappyBird(num_birds=1, gui=False)
        env.pipes.pipes[0].x = 40  # Simula o pipe passando o pássaro
        env.step([False])
        assert env.score == 1  # Score deve aumentar quando o pipe é passado

    def test_get_states(self, mock_env):
        """Testa o método get_states."""
        env = FlappyBird(num_birds=2, gui=False)
        states = env.get_states()
        assert len(states) == 2
        state = states[0]
        assert state.shape == (4,)
        assert state[0] == max((300 - (MockBird.X + MockBird.WIDTH)) / SCREEN_WIDTH, 0)  # distance_x
        assert isinstance(state[1], float)  # Distância para y_upper
        assert isinstance(state[2], float)  # Distância para y_lower
        assert state[3] == 0 / SCREEN_HEIGHT  # Velocidade inicial

    def test_render(self, mock_env):
        """Testa o método render com GUI."""
        env = FlappyBird(num_birds=1, gui=True)
        env.render()
        env.ui.render.assert_called_once_with(env.birds_alive, env.pipes)

    def test_render_no_gui(self, mock_env):
        """Testa o método render sem GUI."""
        env = FlappyBird(num_birds=1, gui=False)
        with pytest.raises(AttributeError):
            env.render()

    def test_close(self, mock_env):
        """Testa o método close."""
        env = FlappyBird(num_birds=2, gui=True)
        env.close()
        assert all(not bird.is_alive for bird in env.birds)
        env.ui.close.assert_called_once()

    def test_check_is_not_closed(self, mock_env):
        """Testa o método _check_is_not_closed."""
        env = FlappyBird(num_birds=1, gui=False)
        env._check_is_not_closed()  # Não deve lançar exceção
        env.birds[0].kill()
        with pytest.raises(EnvClosedError, match='Ambiente já fechado'):
            env._check_is_not_closed()

    def test_repr(self, mock_env):
        """Testa a representação em string."""
        env = FlappyBird(num_birds=3, gui=False)
        assert repr(env) == 'FlappyBird(birds_alive=3, score=0)'