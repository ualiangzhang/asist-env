from gym.envs.registration import register

register(
    id='test_graph-v0',
    entry_point='gym_graph_env.envs:TestGraph',
)
register(
    id='Falcon-v0',
    entry_point='gym_graph_env.envs:FalconGraph',
)
register(
    id='Saturn-v0',
    entry_point='gym_graph_env.envs:SaturnGraph',
)


