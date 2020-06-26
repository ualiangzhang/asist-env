# TODO: Remove this file eventually, no longer needed


import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

MIN_ROOMS = 5
MAX_ROOMS = 10
MAX_DISTANCE = 10
P_ROOMS_CONNECT = 0.1

N_CRIT_VICTIMS = 3
N_NONCRIT_VICTIMS = 7

# TODO: How to incorporate these constants in the environment?
PLAYER_SPEED = 1
TIME = 600

# TODO: add reward/penalty constants?


# TODO: "zones" instead of one big "hallway"/room 0?
class Layout: 
    """
    Layout of the building, represented in a graph data structure. Each room is 
    represented by a node, each doorway is represented by an edge.

    Instantiation generates a random distribution of rooms, at random distances 
    from each other. Every room connects to main "hallway" and some directly
    connect with each other. Assume player's starting location is the main hallway
    """
    def __init__(self):
        self.num_rooms = np.random.randint(MIN_ROOMS, high=MAX_ROOMS+1)
        self.room_labels = np.arange(1, self.num_rooms+1)

        self.G = nx.Graph()
        self.G.add_node(0, gold=0, green=0) # room 0 is the main "hallway"

        for i in self.room_labels:
            self._place_room(i)

        for i in self.room_labels:
            self._connect_rooms(i)

        for _ in range(N_CRIT_VICTIMS):
            self._place_victim('gold')
        for _ in range(N_NONCRIT_VICTIMS):
            self._place_victim('green')

    def _place_room(self, room):
        """Place room at a random distance from main hallway."""
        self.G.add_node(room, gold=0, green=0)
        dist_from_hallway = np.random.randint(1, high=MAX_DISTANCE+1)
        self.G.add_edge(0, room, distance=dist_from_hallway)

    def _place_victim(self, victim_type):
        """Place victim in a random room."""
        room = np.random.choice(self.room_labels)
        current_val = self.G.nodes[room][victim_type]
        nx.set_node_attributes(self.G, {room: {victim_type: current_val+1}})

    # TODO: Doesn't make sense, two connecting rooms must be equidistant from the main hallway.
    def _connect_rooms(self, room):
        """Under a small probability, connect given room to some other one."""
        rooms_connect = np.random.binomial(1, P_ROOMS_CONNECT)
        if rooms_connect:
            adj_room = np.random.choice([i for i in self.room_labels if i != room])
            self.G.add_edge(room, adj_room, distance=0)

    def generate_plot(self):
        """(for debugging purposes) generate a visual plot of the layout."""
        pos = nx.spring_layout(self.G, weight='distance')
        nx.drawing.nx_pylab.draw(self.G, pos, with_labels=True)

        edge_attr = nx.get_edge_attributes(self.G, 'distance')
        nx.draw_networkx_edge_labels(self.G, pos, edge_labels=edge_attr)

        plt.savefig('../debugging/search_rescue_layout.png')

    # TODO
    def update_orientation(self, current_room):
        """Given agent's current room, update 'distance' attribute for all edges."""
        pass


class Agent:
    """
    Agent class. Init with a starting location in the Layout (i.e. room label)
    """
    def __init__(self):
        self.pos = 0
        self.speed = PLAYER_SPEED

    # TODO: Move player according to information passed by args.
    def move(self, current_room):
        pass


env = Layout()
print(env.G.nodes.data())
#env.generate_plot()

# TODO: how to handle observations? information as to where the victims are located?