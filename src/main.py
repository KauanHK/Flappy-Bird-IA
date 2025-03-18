import pygame as pg
from env import FlappyBird
from nn import NeuralNetwork
from nn import crossover, mutate
import numpy as np
import os
from pathlib import Path
import pickle
from datetime import datetime


class QuitPygame(BaseException): ...

class FlappyBirdAI:

    NUM_BIRDS = 100
    MAX_GENERATIONS = 50
    MAX_TIME = 60 * 60  # 60 frames * 60 segundos = 1 minuto
    ELITE_PERCENTAGE = 0.2  # Percentual dos melhores a serem mantidos
    RANDOM_PERCENTAGE = 0.1  # Percentual de novos pássaros aleatórios
    MUTATION_RATE = 0.1  # Taxa de mutação
    MUTATION_STRENGTH = 0.2  # Força da mutação

    SAVE_DIR = Path(__file__).parent.parent / "models" / datetime.now().strftime('%d%m%Y_%H-%M-%S')
    os.makedirs(SAVE_DIR, exist_ok = True)

    def __init__(self) -> None:

        # Inicializar ambiente e redes neurais
        self.env = FlappyBird(num_birds = FlappyBirdAI.NUM_BIRDS, gui = True)
        self.nns = [NeuralNetwork() for _ in range(FlappyBirdAI.NUM_BIRDS)]

        # Inicializar melhores desempenhos e rede neural
        self.best_score_ever = 0
        self.best_steps_ever = 0
        self.best_nn_ever = None

        self._pause = False

    def run(self) -> None:

        print("--------------------------------------------------------------")
        print(f"Iniciando treinamento com {FlappyBirdAI.NUM_BIRDS} pássaros")
        print(f"Elite: {FlappyBirdAI.ELITE_PERCENTAGE:0%}%, Aleatórios: {FlappyBirdAI.RANDOM_PERCENTAGE:0%}%")
        print(f"Taxa de mutação: {FlappyBirdAI.MUTATION_RATE}, Força: {FlappyBirdAI.MUTATION_STRENGTH}")

        generation = 1

        while generation <= FlappyBirdAI.MAX_GENERATIONS and self.env.steps < FlappyBirdAI.MAX_TIME:
            print(f"\n--- Geração {generation}/{FlappyBirdAI.MAX_GENERATIONS} ---")
            try:
                self.run_generation(generation)
            except QuitPygame:
                print('Ambiente fechado...')
                break
            generation += 1

        # Fim do treinamento
        print("\n--- Treinamento concluído ---")
        print(f"Melhor pontuação alcançada: {self.best_steps_ever}")

        # Salvar o melhor modelo final
        if self.best_nn_ever is not None:
            with open(f"{FlappyBirdAI.SAVE_DIR}/best_model_final.pkl", "wb") as f:
                pickle.dump(self.best_nn_ever, f)
            print(f"Modelo final salvo em {FlappyBirdAI.SAVE_DIR}/best_model_final.pkl")

        self.env.close()

    def run_generation(self, generation: int) -> None:

        self.simulate_generation()
        self.update_stats()

        # Ordenar por número de steps
        steps = [bird.steps for bird in self.env.birds]

        # Ordenar índices dos melhores steps, do maior para o menor
        ordered_idx = np.argsort(steps)[::-1]

        # Preparar para a próxima geração
        if generation < FlappyBirdAI.MAX_GENERATIONS:

            # Calcular quantidades
            elite_count = int(FlappyBirdAI.NUM_BIRDS * FlappyBirdAI.ELITE_PERCENTAGE)
            random_count = int(FlappyBirdAI.NUM_BIRDS * FlappyBirdAI.RANDOM_PERCENTAGE)
            crossover_count = FlappyBirdAI.NUM_BIRDS - elite_count - random_count

            print(f"Elite: {elite_count}, Aleatórios: {random_count}, Descendentes: {crossover_count}")

            # Seleção de elite
            elite_nns = [self.nns[i] for i in ordered_idx[:elite_count]]

            # Iniciar nova população repetindo os melhores
            new_population = []
            new_population.extend(elite_nns)

            # Adicionar alguns aleatórios para diversidade
            new_population.extend([NeuralNetwork() for _ in range(random_count)])

            for _ in range(crossover_count):

                parent1, parent2 = np.random.choice(elite_nns, 2, replace = False)
                child = crossover(parent1, parent2)
                mutate(child, FlappyBirdAI.MUTATION_RATE, FlappyBirdAI.MUTATION_STRENGTH)

                new_population.append(child)

            # Atualizar população
            self.nns = new_population

        # Próxima geração
        generation += 1

    def run_events(self) -> None:
        """Executa eventos do pygame."""

        for event in pg.event.get((pg.QUIT, pg.KEYDOWN)):

            if event.type == pg.QUIT:
                # Salvar o melhor modelo antes de sair
                self.update_stats()
                with open(f"{FlappyBirdAI.SAVE_DIR}/best_model_final.pkl", "wb") as f:
                    pickle.dump(self.best_nn_ever, f)
                self.env.close()
                raise QuitPygame

            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                self._pause = not self._pause

    def simulate_generation(self) -> None:

        # Simulação da geração atual
        states = self.env.reset()

        # Loop principal da simulação
        while self.env.birds_alive:
            self.run_events()

            if self._pause:
                continue

            # Coletar ações de todas as redes neurais
            actions = []
            for i, (nn, state, bird) in enumerate(zip(self.nns, states, self.env.birds)):
                if bird.is_alive:
                    actions.append(nn.predict(state.reshape(-1, 1)))
                else:
                    actions.append(0)

            # Executar passo na simulação
            states = self.env.step(actions)

            # Renderizar com informações
            self.env.render()

    def update_stats(self) -> None:

        # Avaliar desempenho
        scores = [bird.score for bird in self.env.birds]
        best_index = np.argmax(scores)

        # Atualizar melhor de todos os tempos
        if scores[best_index] > self.best_steps_ever:
            self.best_steps_ever = scores[best_index]
            self.best_nn_ever = self.nns[best_index]

            # Salvar o novo melhor modelo
            with open(f"{FlappyBirdAI.SAVE_DIR}/best_model_ever.pkl", "wb") as f:
                pickle.dump(self.best_nn_ever, f)

        # Exibir estatísticas
        print(f"Melhor pontuação: {scores[best_index]}")
        print(f"Melhor pontuação de todos os tempos: {self.best_steps_ever}")


if __name__ == '__main__':
    FlappyBirdAI().run()
