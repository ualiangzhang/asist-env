from model import Agent
import numpy as np
from environment import AsistEnvGym
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import itertools


from visualizer import  animate_graph_training

if __name__ == '__main__':
    # data_folder = Path("data")

    # portals_csv = data_folder / "sparky_portals_reduced.csv"
    # rooms_csv = data_folder / "sparky_rooms_reduced.csv"
    # victims_csv = data_folder / "sparky_victims_reduced.csv"

    # portal_data = pd.read_csv(portals_csv)
    # room_data = pd.read_csv(rooms_csv)
    # victim_data = pd.read_csv(victims_csv)

    # env = AsistEnvGym(portal_data, room_data, victim_data, "as")
    env = AsistEnvGym()

    num_of_state = len(env._next_observation())

    # p_gamma_list = [0.99]
    # p_epsilon_end_list = [0.3, 0.15, 0.05]
    # p_batch_size_list = [64, 32, 16]
    # p_eps_dec_list = [5e-4, 1e-4]
    # p_layersize_list = [8, 16, 32, 64]
    # p_lr_list = [3e-4, 1e-4]

    p_gamma_list = [0.98,0.94]
    p_epsilon_end_list = [0.05]
    p_batch_size_list = [32]
    p_eps_dec_list = [3e-5]
    p_layersize_list = [32]
    p_lr_list = [1e-4]

    params = [p_gamma_list, p_epsilon_end_list, p_batch_size_list, p_eps_dec_list, p_layersize_list, p_lr_list]

    index_count = -1
    for par in list(itertools.product(*params)):
        index_count += 1

        p_gamma, p_epsilon_end, p_batch_size, p_eps_dec, p_layersize, p_lr = par

        agent = Agent(gamma=p_gamma, epsilon=1.0, batch_size=p_batch_size, n_actions=num_of_state-2,
                      eps_ends=p_epsilon_end, input_dims=[num_of_state], lr=p_lr, eps_dec=p_eps_dec, layer_size=p_layersize)
        scores, eps_history = [], []
        avg_scores = []
        n_games = 60

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
                observation_, reward, done, info = env.step(action)


                score += reward
                agent.store_transition(observation, action, reward, observation_, done)
                agent.learn()
                observation = observation_
            scores.append(score)
            eps_history.append(agent.epsilon)

            avg_score = np.mean(scores[-50:])
            avg_scores.append(avg_score)

            # if i % 10 == 0 and i > 0:
            #     animate_graph_training(env.visit_node_sequence, portal_data, room_data, victim_data)

            if i % 10 == 0 and i > 0:
                print('episode ', i, 'score %.2f' % score, 'average score %.2f' % avg_score, 'epsilon %.2f' % agent.epsilon, 'victim_saved', len(env.graph.safe_victim_list), "steps", len(env.visit_node_sequence))

        plt.plot(scores, label="raw_scores")
        plt.plot(avg_scores, label="roll_mean_50")
        plt.legend(loc="upper left")
        plt.ylabel("score")
        plt.xlabel("episode")
        plt.savefig(fr'images\RL-runs\7-22\dqn_E{p_epsilon_end}_lr{p_lr}_gamma{p_gamma}_bs{p_batch_size}_ls{p_layersize}_epsd{p_eps_dec}.png')
        plt.clf()

        now = datetime.now().strftime("%A, %B %d, %Y, %I:%M:%S %p")
        with open(rf"images\RL-runs\7-22\log.txt", 'a') as log:
            log.write(f"**Index:** {index_count} \\\n")
            log.write(f"**Time:** {now} \\\n")
            log.write(f"**Parameters:** gamma={p_gamma}, lr={p_lr:.0e}, epsilon=1, eps_ends={p_epsilon_end}, eps_dec={p_eps_dec:.0e}, batch_size={p_batch_size} \\\n")
            log.write(f"**Model:** Deep Q-Network, Epsilon-Decay, Simplified Victim Type, Restricted Action Space, Reduced Environment, Hidden Layer Size {p_layersize} \\\n")
            log.write(f"![DQN](https://github.com/vorugantia/asist-env/blob/master/asist_env/images/RL-runs/7-22\dqn_E{p_epsilon_end}_lr{p_lr}_gamma{p_gamma}_bs{p_batch_size}_ls{p_layersize}_epsd{p_eps_dec}.png) \n\n")