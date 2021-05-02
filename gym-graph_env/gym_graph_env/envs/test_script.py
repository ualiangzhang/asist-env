import gym
from gym import error, spaces, utils
from gym.utils import seeding
import networkx as nx
import matplotlib.pyplot as plt

# This a script to test the parts of the other environment scripts to make sure they are running how expected

class GraphGen1:
    
    @classmethod
    def simple_graph1(cls):
        g = nx.Graph()
        g.add_nodes_from([0,5]) 
        g.add_edges_from([(0,1, {'weight': 8}), (1,2, {'weight': 8}), (2,3, {'weight': 8}), (3,4, {'weight': 8}), (4,5, {'weight': 8}), (1,4, {'weight': 12})])
        g.nodes[5]['Goal'] = 1
        for i in range(5):
            g.nodes[i]['Goal'] = 0

        return g


class TestGraph1(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
    
        super(TestGraph1, self).__init__()
        self.graph = GraphGen1.simple_graph1()
        self.start_node_id = start_node_id
        self.curr_pos = self.graph[start_node_id]
        self.prev_pos = None
        self.total_cost = 0
        self.positive_reward_multiplier = 10
        self.edge_cost_multiplier = 8
        self.visit_node_sequence = []
        self.acrion_space = spaces.Discrete(3)
        self.observation_space = spaces.Discrete(6)
        self.stop_cost = 150
        # now for the definition of the action space and observation space

    def step(self, action):
        
        reward = 0
        done = False
        action_node = None

        # determining how to deal with the actions is difficult, right now
        # we are treating picking an action value beyond the number of connections
        # as a waste of time but allowing it. 
        connections = len(self.graph.neighbors(self.curr_pos))

        if action > connections:
            reward -= 100
            self.total_cost += 12
            action_node = self.curr_pos
        else:
            for index, n_node in enumerate(self.graph.neighbors(self.curr_pos)):
                if action == index:
                    action_node = n_node
        

        self.visit_node_sequence.append(action_node.id)
        edge_dist = self.graph.get_edge_cost(self.curr_pos, action_node) # this function might need some work
        self.prev_pos = self.curr_pos
        self.curr_pos = action_node
        reward -= edge_dist * self.edge_cost_multiplier
        self.total_cost += edge_dist

        if self.curr_pos['Goal'] == 1:
            reward += self.positive_reward_multiplier * 50

        if self.total_cost > self.stop_cost or self.curr_pos['Goal'] == 1: 
            done = True

        return self.curr_pos, reward, done, {}

    def reset(self):
        
        self.curr_pos = self.graph[self.start_node_id]
        self.total_cost = 0
        self.prev_pos = Noneself.visit_node_sequence.clear()

        return self.curr_pos


    def render(self, mode='human'):
        
        pass


g1 = GraphGen1.simple_graph1()
pos = nx.spectral_layout(g1)
labels = nx.get_node_attributes(g1, 'Goal')
print(g1[1][2]['weight']) # this pulls the weight between the nodes
print(g1[2][5]['weight'])
nx.draw(g1, pos)
nx.draw_networkx_labels(g1, pos, labels=labels)
nx.draw_networkx_edge_labels(g1, pos, edge_labels=nx.get_edge_attributes(g1, 'weight'))
plt.savefig("test.png")



