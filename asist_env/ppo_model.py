import torch
import torch.nn as nn
from torch.distributions import Categorical
from environment import AsistEnvGym
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import argparse
# from visualizer import animate_graph_training
from visualizer import plot_graph

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

class Memory:
    def __init__(self):
        self.actions = []
        self.states = []
        self.logprobs = []
        self.rewards = []
        self.is_terminals = []

    def clear_memory(self):
        del self.actions[:]
        del self.states[:]
        del self.logprobs[:]
        del self.rewards[:]
        del self.is_terminals[:]

class ActorCritic(nn.Module):
    def __init__(self, state_dim, action_dim, n_latent_var):
        super(ActorCritic, self).__init__()

        # actor
        self.action_layer = nn.Sequential(
            nn.Linear(state_dim, n_latent_var),
            nn.ReLU(),
            nn.Linear(n_latent_var, n_latent_var),
            nn.ReLU(),
            nn.Linear(n_latent_var, action_dim),
            nn.Softmax(dim=-1)
        )

        # critic
        self.value_layer = nn.Sequential(
            nn.Linear(state_dim, n_latent_var),
            nn.ReLU(),
            nn.Linear(n_latent_var, n_latent_var),
            nn.ReLU(),
            nn.Linear(n_latent_var, 1)
        )

    def forward(self):
        raise NotImplementedError

    def act(self, state, memory):
        state = torch.from_numpy(state).float().to(device)
        action_probs = self.action_layer(state)
        # mask = state[:-2].ge(0.1).float().to(device)
        # dist = Categorical(action_probs * mask)
        dist = Categorical(action_probs)
        action = dist.sample()

        memory.states.append(state)
        memory.actions.append(action)
        memory.logprobs.append(dist.log_prob(action))

        return action.item()

    def evaluate(self, state, action):
        action_probs = self.action_layer(state)
        dist = Categorical(action_probs)

        action_logprobs = dist.log_prob(action)
        dist_entropy = dist.entropy()

        state_value = self.value_layer(state)

        return action_logprobs, torch.squeeze(state_value), dist_entropy

class PPO:
    def __init__(self, state_dim, action_dim, n_latent_var, lr, betas, gamma, K_epochs, eps_clip):
        self.lr = lr
        self.betas = betas
        self.gamma = gamma
        self.eps_clip = eps_clip
        self.K_epochs = K_epochs

        self.policy = ActorCritic(state_dim, action_dim, n_latent_var).to(device)
        self.optimizer = torch.optim.Adam(self.policy.parameters(), lr=lr, betas=betas)
        self.policy_old = ActorCritic(state_dim, action_dim, n_latent_var).to(device)
        self.policy_old.load_state_dict(self.policy.state_dict())

        self.MseLoss = nn.MSELoss()

    def update(self, memory):
        # Monte Carlo estimate of state rewards:
        rewards = []
        discounted_reward = 0
        for reward, is_terminal in zip(reversed(memory.rewards), reversed(memory.is_terminals)):
            if is_terminal:
                discounted_reward = 0
            discounted_reward = reward + (self.gamma * discounted_reward)
            rewards.insert(0, discounted_reward)

        # Normalizing the rewards:
        rewards = torch.tensor(rewards).to(device)
        rewards = (rewards - rewards.mean()) / (rewards.std() + 1e-5)

        # convert list to tensor
        old_states = torch.stack(memory.states).to(device).detach()
        old_actions = torch.stack(memory.actions).to(device).detach()
        old_logprobs = torch.stack(memory.logprobs).to(device).detach()

        # Optimize policy for K epochs:
        for _ in range(self.K_epochs):
            # Evaluating old actions and values :
            logprobs, state_values, dist_entropy = self.policy.evaluate(old_states, old_actions)

            # Finding the ratio (pi_theta / pi_theta__old):
            ratios = torch.exp(logprobs - old_logprobs.detach())

            # Finding Surrogate Loss:
            advantages = rewards - state_values.detach()
            surr1 = ratios * advantages
            surr2 = torch.clamp(ratios, 1-self.eps_clip, 1+self.eps_clip) * advantages
            loss = -torch.min(surr1, surr2) + 0.5*self.MseLoss(state_values, rewards) - 0.01*dist_entropy

            # take gradient step
            self.optimizer.zero_grad()
            loss.mean().backward()
            self.optimizer.step()

        # Copy new weights into old policy:
        self.policy_old.load_state_dict(self.policy.state_dict())

def main():

    ############## creating environment ##############
    data_folder = Path("data")

    portals_csv = data_folder / "sparky_portals.csv"
    rooms_csv = data_folder / "sparky_rooms.csv"
    victims_csv = data_folder / "sparky_victims.csv"

    portal_data = pd.read_csv(portals_csv)
    room_data = pd.read_csv(rooms_csv)
    victim_data = pd.read_csv(victims_csv)

    env = AsistEnvGym(portal_data, room_data, victim_data, "as", random_victim=False)
    # state_dim = len(env._next_observation())
    # state_dim = 7+2+2+1+2+1+3
    state_dim = 7+2+2+1+1+3

    ############## parsing parameter ##############
    parser = argparse.ArgumentParser(description='hyper parameters for PPO')
    parser.add_argument('-lr', type=float, help='Learning Rate')
    parser.add_argument('-clip', type=float, help='Epsilon Tick')
    parser.add_argument('-ut', '--update_timestep', type=int, help='update policy every n timesteps')
    parser.add_argument('-k','--k_epochs', type=int, help='update policy for K epochs')
    parser.add_argument('-me','--max_episodes', type=int, help='how many episodes')
    args = parser.parse_args()


    ############## Hyperparameters ##############
    # action_dim = state_dim - 2
    action_dim = 9
    render = False
    solved_reward = 800000         # stop training if avg_reward > solved_reward
    log_interval = 20           # print avg reward in the interval
    max_episodes = 20        # max training episodes
    max_timesteps = 20000         # max timesteps in one episode
    n_latent_var = 32           # number of variables in hidden layer
    update_timestep = 1024      # update policy every n timesteps
    lr = 3e-4
    betas = (0.9, 0.999)
    gamma = 0.99                # discount factor
    K_epochs = 10                # update policy for K epochs
    eps_clip = 0.2              # clip parameter for PPO
    # random_seed = None

    #############################################
    if args.lr is not None:
        lr = args.lr
    if args.clip is not None:
        eps_clip = args.clip
    if args.update_timestep is not None:
        update_timestep = args.update_timestep
    if args.k_epochs is not None:
        K_epochs = args.k_epochs
    if args.max_episodes is not None:
        max_episodes = args.max_episodes


    # if random_seed:
    #     torch.manual_seed(random_seed)
    #     env.seed(random_seed)

    memory = Memory()
    ppo = PPO(state_dim, action_dim, n_latent_var, lr, betas, gamma, K_epochs, eps_clip)
    print(f"episode={max_episodes}, lr={lr}, ls={n_latent_var}, ut={update_timestep}, ke={K_epochs}, clip={eps_clip}")

    # logging variables
    running_reward = 0
    # avg_length = 0
    timestep = 0

    # training loop
    scores_list = []
    # saved_victims_list = []
    good_path_dict = dict()
    nodes_set = {'as'}

    # visited_freq = dict()
    # for node in env.graph.nodes_list:
    #     visited_freq[node.id] = 0

    max_reward = -9999999
    max_victim_saved = -1

    for i_episode in range(1, max_episodes+1):
        raw_score = 0
        state = env.reset_victims()
        # state = env.reset()
        # plot_graph(env.graph, pop_out=True)
        # visited_freq['as'] += 1
        for t in range(max_timesteps):
            timestep += 1

            # Running policy_old:
            action = ppo.policy_old.act(state, memory)
            state, reward, done, info = env.step(action)
            nodes_set.add(env.curr_pos.id)
            # visited_freq[env.curr_pos.id] += 1

            # Saving reward and is_terminal:
            memory.rewards.append(reward)
            memory.is_terminals.append(done)

            # update if its time
            if timestep % update_timestep == 0:
                ppo.update(memory)
                memory.clear_memory()
                timestep = 0

            running_reward += reward
            raw_score += reward

            # if render:
            #     env.render()
            if done:
                break

        # avg_length += t
        scores_list.append(raw_score)
        # saved_victims_list.append(len(env.graph.safe_victim_list))

        # stop training if avg_reward > solved_reward
        if running_reward > (log_interval*solved_reward):
            print("########## Solved! ##########")
            torch.save(ppo.policy.state_dict(), './PPO_{}.pth'.format("Asist"))
            break

        if raw_score > max_reward:
            max_reward = raw_score
        if len(env.graph.safe_victim_list) > max_victim_saved:
            max_victim_saved = len(env.graph.safe_victim_list)


        # logging
        if i_episode % log_interval == 0 or max_reward == raw_score:
            # avg_length = int(avg_length/log_interval)
            running_reward = int((running_reward/log_interval))

            print('Episode {:<6} avg_reward: {:<5.0f} reward: {:<5.0f} max_reward: {:<5.0f} victims_saved: {:<2} max_victim_saved: {:<2} steps: {:<3} total_cost: {:<4.0f} unique_node: {:>3}/123 all_nodes: {:>3}/123'.format(i_episode, running_reward, raw_score, max_reward, len(env.graph.safe_victim_list), max_victim_saved, len(env.visit_node_sequence), env.total_cost, len(set(env.visit_node_sequence)), len(nodes_set)))
            # animate_graph_training(env.visit_node_sequence, portal_data, room_data, victim_data)
            running_reward = 0
            avg_length = 0

        num_of_saved = len(env.graph.safe_victim_list)
        if num_of_saved >= 20:
            if num_of_saved in good_path_dict:
                if len(env.visit_node_sequence) < len(good_path_dict[num_of_saved]):
                    good_path_dict[num_of_saved] = env.visit_node_sequence.copy()
            else:
                good_path_dict[num_of_saved] = env.visit_node_sequence.copy()

    # env_run = AsistEnvGym(portal_data, room_data, victim_data, "as")
    # after_path_list = list()
    # for i in range(10):
    #     state = env.reset()
    #     done = False
    #     while not done:
    #         action = ppo.policy_old.act(state, memory)
    #         state, reward, done, info = env_run.step(action)
    #     after_path_list.append(env_run.visit_node_sequence.copy())

    avg_scores = np.zeros(max_episodes)
    # avg_saved_victim = np.zeros(max_episodes)
    for t in range(max_episodes):
        avg_scores[t] = np.mean(scores_list[max(0, t-200):(t+1)])
        # avg_saved_victim[t] = np.mean(saved_victims_list[max(0, t-40):(t+1)])

    # with open("graphdata_ppo.txt", 'w') as gd:
    #     gd.write(str(list(avg_scores)))

    # with open(f"volkan_room_exploration_realtime_hastriagetimecost_reward_ls{n_latent_var}_ut{update_timestep}_clip{eps_clip}_50000_2000.txt", 'w') as gd:
    #    gd.write(str(good_path_dict))

    # with open("volkan_random_victim.txt", 'w') as gd:
    #     gd.write(str(after_path_list))

    # print(visited_freq)
    print(f"room exploration only, realtime reward, has triage time cost")
    # plt.plot(scores_list, label="raw_scores")
    # fig, ax1 = plt.subplots()
    # ax1.set_xlabel('episode')
    # ax1.set_ylabel('score')
    # ax1.plot(avg_scores, label="score_avg100", color="C0")
    # plt.legend(loc="upper left")

    # ax2 = ax1.twinx()
    # ax2.set_ylabel('saved_victims')
    # ax2.plot(avg_saved_victim, label="saved", color="C1")

    # plt.savefig("PPO_newAction_fullMap.png")

    #plt.plot(avg_scores, label="roll_mean_200")
    #plt.legend(loc="upper left")
    #plt.ylabel("score")
    #plt.xlabel("episode")
    #plt.savefig(f"random_victim_distribution.png")
    # plt.savefig(f'ppo_clip{str(eps_clip).replace(".","")}_lr{str(lr).replace(".","")}_ut{update_timestep}_KEpoch{K_epochs}.png')

if __name__ == '__main__':
    main()
