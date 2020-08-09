from gym.envs.registration import register

register(
    id='AsistEnv-v0',
    entry_point='AsistEnv.asist_env:AsistEnvGym'
)