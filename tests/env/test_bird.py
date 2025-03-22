import pytest
from ..conftest import MockMask

from src.env import Bird, Pipe
from src.env.bird import DeadBirdError
from src.env.utils import SCREEN_CENTER_Y, SCREEN_WIDTH


def test_initialization(default_bird):
    """Teste de inicialização com valores padrão"""

    assert default_bird.y == SCREEN_CENTER_Y
    assert default_bird.velocity_y == 0
    assert default_bird.steps == 0
    assert default_bird.is_alive
    assert default_bird.score == 0

    # Teste de inicialização com y personalizado
    custom_y = 200
    bird = Bird(y = custom_y)
    assert bird.y == custom_y

def test_update_no_action(default_bird):
    """Teste de atualização sem ação (não pular)"""

    pipe = Pipe.new_pipe(SCREEN_WIDTH)

    # Estado inicial
    initial_y = default_bird.y

    # Atualizar sem pular
    default_bird.update(0, pipe, False)

    # Verificar se a gravidade foi aplicada
    assert default_bird.velocity_y > 0
    assert default_bird.y > initial_y  # Y deve aumentar (cair)
    assert default_bird.steps == 1  # Deve incrementar os passos
    assert default_bird.is_alive == True  # Deve continuar vivo
    assert default_bird.score == 0  # Não deve pontuar

def test_update_with_jump(default_bird):
    """Teste de atualização com ação de pular"""

    bird = default_bird
    pipe = Pipe.new_pipe(x = SCREEN_WIDTH)

    initial_y = bird.y

    # Atualizar com pulo
    bird.update(1, pipe, False)

    # Verificar se o impulso foi aplicado
    assert bird.velocity_y == Bird.LIFT
    assert bird.y < initial_y
    assert bird.is_alive
    assert bird.steps == 1
    assert bird.score == 0

def test_update_with_score(default_bird):
    """Teste de atualização com pontuação"""

    bird = default_bird
    pipe = Pipe.new_pipe(x = SCREEN_WIDTH)

    # Atualizar e pontuar
    bird.update(0, pipe, True)

    assert bird.score == 1
    assert bird.steps == 1

@pytest.mark.parametrize(
    'action',
    ((2,), ('jump',), (0.5,))
)
def test_update_invalid_action(action, default_bird):
    """Teste com ação inválida"""

    bird = default_bird
    pipe = Pipe.new_pipe(x = SCREEN_WIDTH)

    # Deve lançar ValueError para ações inválidas
    with pytest.raises(ValueError):
        bird.update(action, pipe, False)

def test_kill(default_bird):
    """Teste do método kill"""

    bird = default_bird
    assert bird.is_alive
    bird.kill()
    assert not bird.is_alive

def test_update_dead_bird(default_bird):
    """Teste de atualização com pássaro morto"""

    bird = default_bird
    pipe = Pipe.new_pipe(x = SCREEN_WIDTH)

    initial_y = bird.y
    initial_velocity_y = bird.velocity_y

    bird.kill()

    with pytest.raises(DeadBirdError):
        bird.update(1, pipe, True)

    # Verificar se nada mudou
    assert bird.y == initial_y
    assert bird.velocity_y == initial_velocity_y
    assert not bird.is_alive

def test_collision_with_floor(default_bird):
    """Teste de colisão com o chão"""

    # Posicionar abaixo do chão
    bird = Bird(y = Bird.FLOOR + 10)
    pipe = Pipe.new_pipe(x = SCREEN_WIDTH)

    bird.update(0, pipe, False)
    assert bird.is_alive == False

def test_collision_with_ceiling(default_bird):
    """Teste de colisão com o teto"""

    # Posicionar acima do teto
    bird = Bird(y = -Bird.HEIGHT)
    pipe = Pipe.new_pipe(x = SCREEN_WIDTH)

    bird.update(0, pipe, False)

    assert bird.is_alive == False

def test_collision_with_pipe(default_bird):
    """Teste de colisão com o cano"""

    bird = default_bird
    pipe = Pipe(x = Bird.X, y_lower = bird.y)

    # Simular colisão
    MockMask.set_overlap_return_value(collides = True)
    bird.update(0, pipe, False)
    assert not bird.is_alive

def test_no_collision_distant_pipe(default_bird):
    """Teste sem colisão com cano distante"""

    bird = default_bird

    # Cano distante
    pipe = Pipe.new_pipe(x = Bird.X + Bird.WIDTH + 50)

    MockMask.set_overlap_return_value(collides = False)
    bird.update(0, pipe, False)

    assert bird.is_alive
