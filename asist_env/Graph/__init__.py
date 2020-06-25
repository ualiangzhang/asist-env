import networkx
from .Nodes import *


class Graph(networkx.Graph):
    def __init__(self):
        super(Graph, self).__init__()
        self.room_list = []
        self.portal_list = []
        self.victim_list = []
        self.yellow_victim_list = []
        self.green_victim_list = []
        self.dead_victim_list = []

    def new_node(self, name, node_type, *args, **kwargs):

        assert isinstance(node_type, NodeType)
        assert

        if node_type == NodeType.Portal:
            name = "P" + str(len(self.portal_list)) + "_" + name
            node = PortalNode(name)
        elif node_type == NodeType.Victim:
            name = "V" +

        elif node_type == NodeType.Room:
            name = "R" + str(len(self.room_list)) + ""

        self.add_node()

    def add_link(self, node1, node2):
        pass


    def get_neighbor(self):
        pass

