from model import Agent
import numpy as np
from environment import AsistEnv
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

if __name__ == '__main__':
    data_folder = Path("data")

    portals_csv = data_folder / "sparky_portals.csv"
    rooms_csv = data_folder / "sparky_rooms.csv"
    victims_csv = data_folder / "sparky_victims.csv"

    portal_data = pd.read_csv(portals_csv)
    room_data = pd.read_csv(rooms_csv)
    victim_data = pd.read_csv(victims_csv)

    env = AsistEnv(portal_data, room_data, victim_data, "as")

    num_of_state = len(env.get_observation())

    agent = Agent(gamma=0.99, epsilon=1.0, batch_size=64, n_actions=num_of_state-1,
                  eps_ends=0.05, input_dims=[num_of_state], lr=0.003, eps_dec=5e-5)
    scores, eps_history = [], []
    avg_scores = []
    n_games = 1000

    for i in range(n_games):
        score = 0
        done = False
        observation = env.reset()
        while not done:
            # print(env.get_unorganized_observation_debug())
            # for idx, obs in enumerate(env.get_unorganized_observation_debug()):
            #     print(str(obs + (idx,)), end=" ")
            #     if idx %5 == 0 and idx != 0:
            #         print()
            action = agent.choose_action_narrow(observation)
            observation_, reward, done = env.step_unorganized(action)
            score += reward
            agent.store_transition(observation, action, reward, observation_, done)
            agent.learn()
            observation = observation_
        scores.append(score)
        eps_history.append(agent.epsilon)

        avg_score = np.mean(scores[-50:])
        avg_scores.append(avg_score)

        print('episode ', i, 'score %.2f' % score, 'average score %.2f' % avg_score, 'epsilon %.2f' % agent.epsilon, 'victim_saved', len(env.graph.safe_victim_list))

    plt.plot(scores, label="raw_scores")
    plt.plot(avg_scores, label="roll_mean_50")
    plt.legend(loc="upper left")
    plt.ylabel("score")
    plt.xlabel("episode")
    plt.savefig('dqn.png')