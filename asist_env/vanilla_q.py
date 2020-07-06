from environment import AsistEnv
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def max_action(Q, state, action_space):
    values = np.array([Q[state, action]] for action in action_space)
    action = np.argmax(values)
    return action_space[action]

def random_action(performance_space, action_node_space):
    return (np.random.choice(performance_space), np.random.choice(action_node_space))

def possible_action(env):
    pass


if __name__ == '__main__':
    data_folder = Path("data")

    portals_csv = data_folder / "sparky_portals.csv"
    rooms_csv = data_folder / "sparky_rooms.csv"
    victims_csv = data_folder / "sparky_victims.csv"

    portal_data = pd.read_csv(portals_csv)
    room_data = pd.read_csv(rooms_csv)
    victim_data = pd.read_csv(victims_csv)

    env = AsistEnv(portal_data, room_data, victim_data, "as")

    max_episode_steps = 1000
    n_games = 50000
    alpha = 0.1
    gamma = 0.99
    eps = 1.0

    performance_space = [0, 1, 2]
    action_node_space = list(range(env.get_victim_list_size()))

    action_space = [(p, a) for p in performance_space for a in action_node_space]

    Q = {}
    states = set()
    # for state in states:
    #     for action in action_space:
    #         Q[state, action] = 0

    score = 0
    total_rewards = np.zeros(n_games)
    for i in range(n_games):
        done = False
        state = env.reset()
        states.add(state)
        for a in action_space:
            Q[state, a] = 0
        if i % 50 == 0 and i > 0:
            print('episode ', i, 'score ', score, 'epsilon %.3f' % eps)
        score = 0
        for iter in range(max_episode_steps):
            if np.random.random() < eps:
                action = random_action(performance_space, action_node_space)
            else:
                action = max_action(Q, state, action_space)

            # action = random_action(performance_space, action_node_space) if np.random.random() < eps \
            #     else max_action(Q, state, action_space)
            # print(action)
            state_, reward, done = env.step(action)
            if state_ not in states:
                states.add(state_)
                for a in action_space:
                    Q[state_, a] = 0
            score += reward
            action_ = max_action(Q, state_, action_space)
            Q[state, action] = Q[state, action] + \
                               alpha*(reward + gamma*Q[state_, action_] - Q[state, action])
            state = state_
            if done:
                break
        total_rewards[i] = score
        eps = eps - 2/n_games if eps > 0.01 else 0.01

    mean_rewards = np.zeros(n_games)
    for t in range(n_games):
        mean_rewards[t] = np.mean(total_rewards[max(0, t-50):(t+1)])
    plt.plot(mean_rewards)
    plt.savefig('vanilla.png')