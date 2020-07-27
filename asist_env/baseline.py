import os
from pathlib import Path

from environment import AsistEnvGym

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from stable_baselines3 import PPO
from stable_baselines3.ppo import MlpPolicy
from stable_baselines3.common import results_plotter
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.results_plotter import load_results, ts2xy, plot_results
from stable_baselines3.common.noise import NormalActionNoise
from stable_baselines3.common.callbacks import BaseCallback


class SaveOnBestTrainingRewardCallback(BaseCallback):
    """
    Callback for saving a model (the check is done every ``check_freq`` steps)
    based on the training reward (in practice, we recommend using ``EvalCallback``).

    :param check_freq: (int)
    :param log_dir: (str) Path to the folder where the model will be saved.
      It must contains the file created by the ``Monitor`` wrapper.
    :param verbose: (int)
    """
    def __init__(self, check_freq: int, log_dir: str, verbose=1):
        super(SaveOnBestTrainingRewardCallback, self).__init__(verbose)
        self.check_freq = check_freq
        self.log_dir = log_dir
        self.save_path = os.path.join(log_dir, 'best_model')
        self.best_mean_reward = -np.inf

    def _init_callback(self) -> None:
        # Create folder if needed
        if self.save_path is not None:
            os.makedirs(self.save_path, exist_ok=True)

    def _on_step(self) -> bool:
        if self.n_calls % self.check_freq == 0:

            # Retrieve training reward
            x, y = ts2xy(load_results(self.log_dir), 'timesteps')
            if len(x) > 0:
                # Mean training reward over the last 100 episodes
                mean_reward = np.mean(y[-100:])
                if self.verbose > 0:
                    print("Num timesteps: {}".format(self.num_timesteps))
                    print("Best mean reward: {:.2f} - Last mean reward per episode: {:.2f}".format(self.best_mean_reward, mean_reward))

                # New best model, you could save the agent here
                if mean_reward > self.best_mean_reward:
                    self.best_mean_reward = mean_reward
                    # Example for saving best model
                    if self.verbose > 0:
                        print("Saving new best model to {}".format(self.save_path))
                    self.model.save(self.save_path)

        return True

if __name__ == '__main__':
    log_dir = "tmp/"
    os.makedirs(log_dir, exist_ok=True)


    data_folder = Path("data")

    portals_csv = data_folder / "sparky_portals.csv"
    rooms_csv = data_folder / "sparky_rooms.csv"
    victims_csv = data_folder / "sparky_victims.csv"

    portal_data = pd.read_csv(portals_csv)
    room_data = pd.read_csv(rooms_csv)
    victim_data = pd.read_csv(victims_csv)

    # The algorithms require a vectorized environment to run
    # env = DummyVecEnv([lambda: AsistEnvGym(portal_data, room_data, victim_data, "as")])

    env = AsistEnvGym(portal_data, room_data, victim_data, "as")
    env = Monitor(env, log_dir)

    n_actions = env.action_space.shape
    action_noise = NormalActionNoise(mean=np.zeros(n_actions), sigma=0.1 * np.ones(n_actions))


    model = PPO(MlpPolicy, env, verbose=1)
    callback = SaveOnBestTrainingRewardCallback(check_freq=1000, log_dir=log_dir)


    # model = DQN(MlpPolicy, env, verbose=1)
    timeSteps = 80000
    model.learn(total_timesteps=timeSteps, callback=callback)


    plot_results([log_dir], timeSteps, results_plotter.X_TIMESTEPS, "TD3 LunarLander")
    plt.show()


    # obs = env.reset()

    # score = 0
    # done = False
    # while not done:
    #     action, _states = model.predict(obs, deterministic=True)
    #     obs, rewards, done, info = env.step(action)
    #     score += rewards
    #     env.render()
    # with open("tmp.txt", 'w') as ff:
    #     g = ff.write(str(env.visit_node_sequence))
    # print(env.visit_node_sequence)
    # print("Victim_saved:", len(env.graph.safe_victim_list))
    # print("steps:", len(env.visit_node_sequence))
    # print(score)