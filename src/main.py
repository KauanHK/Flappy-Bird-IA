def main() -> None:

    import pygame as pg
    from env import FlappyBird
    from nn import NeuralNetwork, crossover, mutate
    import numpy as np

    num_birds = 100
    generations = 20
    max_score = 100

    env = FlappyBird(num_birds = num_birds, gui = True)
    nns = [NeuralNetwork() for _ in range(num_birds)]

    generation = 0
    while generation < generations and env.score < max_score:

        states = env.reset()
        while not env.done:

            if pg.event.get(pg.QUIT):
                env.close()
                return

            actions = []
            for nn, state in zip(nns, states):
                actions.append(nn.predict(np.array(state).reshape(-1, 1)))

            states = env.step(actions)
            env.render()
            # print(states)

        ordered_index = sorted(list(range(env.num_birds)), key = lambda i: env.frames_alive[i], reverse = True)
        print(ordered_index)
        best_nns = [nns[i] for i in ordered_index[:20]]

        new_nns = [NeuralNetwork() for _ in range(num_birds - 40)]
        new_nns.extend(best_nns)
        while len(new_nns) < num_birds:

            nn1, nn2 = np.random.choice(best_nns, 2, replace = False)
            nn = crossover(nn1, nn2)
            mutate(nn)
            new_nns.append(nn)


        generation += 1


if __name__ == '__main__':
    main()
