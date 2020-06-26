import networkx
from .Nodes import *
from collections.abc import Iterable


class Graph(networkx.Graph):
    """
        A networkx Graph
    """
    def __init__(self):
        super(Graph, self).__init__()
        self.nodes_list = []

        self.room_list = []
        self.portal_list = []
        self.victim_list = []

        self.green_victim_list = []
        self.yellow_victim_list = []
        self.safe_victim_list = []
        self.dead_victim_list = []

        self.id2node = {}

        self.victimType2list = {
            VictimType.Green: self.green_victim_list,
            VictimType.Yellow: self.yellow_victim_list,
            VictimType.Safe: self.safe_victim_list,
            VictimType.Dead: self.dead_victim_list,
        }

    def add_victim(self, victim_type, id=None, name=None):
        """ Register a victim node to graph and append the corresponding lists

        :param id: the victim id, if id not give, the method will auto generate one
        :param name: the name of the Victim such as Jason. (Default None)
        :param victim_type: Must be one of [Yellow, Green, Dead, Safe]
        :return: the victim node constructed
        """
        assert id is None or isinstance(id, str)
        assert name is None or isinstance(name, str)
        assert isinstance(victim_type, VictimType)

        node_id = "V"

        if victim_type == VictimType.Green:
            node_id = "G" + str(len(self.green_victim_list))
        elif victim_type == VictimType.Yellow:
            node_id = "Y" + str(len(self.yellow_victim_list))
        elif victim_type == VictimType.Safe:
            node_id = "S" + str(len(self.safe_victim_list))
        elif victim_type == VictimType.Dead:
            node_id = "D" + str(len(self.dead_victim_list))

        if id is not None:
            node_id = id

        node = VictimNode(node_id, name, victim_type)
        self.victimType2list[victim_type].append(node)
        self.victim_list.append(node)
        self.nodes_list.append(node)
        self.id2node[node_id] = node

        self.add_node(node)

        return node

    def add_portal(self, connected_room_ids, id=None, name=None, is_pair=True):
        """ Add portal (pair)

        :param id: the portal id, if id not give, the method will auto generate one
        :param name: name of the portal, if any
        :param is_pair: if it is a pair of portals. The start is not pair
        :param connected_room: the room that the portal is connected to
        :return: the created portal node
        """
        assert id is None or isinstance(id, str)
        assert name is None or isinstance(name, str)
        assert isinstance(is_pair, bool)
        assert isinstance(connected_room_ids, str) or isinstance(connected_room_ids, tuple) and \
               all(isinstance(r, str) for r in connected_room_ids)

        node_id = id if id is not None else "P" + str(len(self.portal_list))


    def add_room(self, name=None):




    def add_link(self, node1, node2):
        pass


    def get_neighbor(self):
        pass
