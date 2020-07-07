from environment import AsistEnv
from graph.Nodes import NodeType
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import random

def max_action(Q, state, action_space):
    values = np.array([Q[state, action]] for action in action_space)
    action = np.argmax(values)
    return action_space[action]

def random_action(performance_space, action_node_space):
    return (np.random.choice(performance_space), np.random.choice(action_node_space))

def max_action_limit(Q, state, env):
    nei = [n for n in env.graph.get_neighbors(env.curr_pos)]
    max_action = tuple()
    max_action_value = -100000000
    for n in nei:
        p = None
        if n.type == NodeType.Portal:
            if env.curr_pos.type == NodeType.Portal and \
                    n.is_same_portal(env.curr_pos):
                p = 1
            else:
                p = 0
        elif n.type == NodeType.Victim:
            p = 2
        elif n.type == NodeType.Room:
            p = 0
        action = (p, env.graph.nodes_list.index(n))
        value = Q[state, action]
        if value > max_action_value:
            max_action_value = value
            max_action = action
    return max_action

def possible_action(env):
    nei = [n for n in env.graph.get_neighbors(env.curr_pos)]
    act = random.choice(nei)

    if act.type == NodeType.Portal:
        if env.curr_pos.type == NodeType.Portal and \
                act.is_same_portal(env.curr_pos):
            p = 1
        else:
            p = 0
    elif act.type == NodeType.Victim:
        p = 2
    elif act.type == NodeType.Room:
        p = 0
    return p, env.graph.nodes_list.index(act)

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
    n_games = 10000
    alpha = 0.1
    gamma = 0.99
    eps = 0.3

    inspect_interval = 50

    performance_space = [0, 1, 2]
    action_node_space = list(range(len(env.graph.nodes_list)))

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
        if i % inspect_interval == 0 and i > 0:
            print('episode ', i, 'score ', score, 'epsilon %.3f' % eps, end=" ")
        score = 0
        for iter in range(max_episode_steps):
            if np.random.random() < eps:
                # action = random_action(performance_space, action_node_space)
                action = possible_action(env)
            else:
                # action = max_action(Q, state, action_space)
                action = max_action_limit(Q, state, env)

            # action = random_action(performance_space, action_node_space) if np.random.random() < eps \
            #     else max_action(Q, state, action_space)
            # print(action)
            state_, reward, done = env.step(action)
            # print(action, state_)
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
        # eps = eps - 2/n_games if eps > 0.01 else 0.01
        if i % inspect_interval == 0 and i > 0:
            print(" victims_saved:", len(env.graph.safe_victim_list))

    mean_rewards = np.zeros(n_games)
    for t in range(n_games):
        mean_rewards[t] = np.mean(total_rewards[max(0, t-inspect_interval):(t+1)])
    plt.plot(mean_rewards)
    plt.ylabel("score")
    plt.xlabel("episode")
    plt.savefig('vanilla.png')