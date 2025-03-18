def main() -> None:

    import pygame as pg
    from env import FlappyBird
    from nn import NeuralNetwork, crossover, mutate
    import numpy as np

    num_birds = 500
    generations = 20
    max_time = 60 * 60

    env = FlappyBird(num_birds = num_birds, gui = True)
    nns = [NeuralNetwork() for _ in range(num_birds)]

    generation = 0
    while generation < generations and env.steps < max_time:

        states = env.reset()
        birds_done = [False] * num_birds
        while not env.done:

            if pg.event.get(pg.QUIT):
                env.close()
                return

            actions = []
            for nn, state, bird_done in zip(nns, states, birds_done):
                if bird_done:
                    actions.append(0)
                else:
                    actions.append(nn.predict(np.array(state).reshape(-1, 1)))

            states, birds_done = env.step(actions)
            print(str(states[0]).ljust(80), end = '\r')
            env.render()

        ordered_index = sorted(list(range(env.num_birds)), key = lambda i: env.birds[i].steps, reverse = True)
        best_nns = [nns[i] for i in ordered_index[:len(ordered_index) // 5]]

        new_nns = [NeuralNetwork() for _ in range(round(num_birds*0.6))]
        new_nns.extend(best_nns)
        while len(new_nns) < num_birds:

            nn1, nn2 = np.random.choice(best_nns, 2, replace = False)
            nn = crossover(nn1, nn2)
            mutate(nn)
            new_nns.append(nn)


        generation += 1


if __name__ == '__main__':
    main()
