import gym
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3 import PPO
from stable_baselines3.ppo import MlpPolicy
from environment import AsistEnvGym
import pandas as pd
from pathlib import Path

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
model = PPO(MlpPolicy, env, verbose=1)
model.learn(total_timesteps=20000)
obs = env.reset()

score = 0
for i in range(2000):
    action, _states = model.predict(obs)
    obs, rewards, done, info = env.step(action)
    score += rewards
    env.render()
print(score)