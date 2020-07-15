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
model.learn(total_timesteps=200000)
obs = env.reset()

score = 0
done = False
while not done:
    action, _states = model.predict(obs)
    obs, rewards, done, info = env.step(action)
    score += rewards
    env.render()
with open("tmp.txt", 'w') as ff:
    g = ff.write(str(env.visit_node_sequence))
print(env.visit_node_sequence)
print("Victim_saved:", len(env.graph.safe_victim_list))
print("steps:", len(env.visit_node_sequence))
print(score)