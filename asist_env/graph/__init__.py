import networkx as nx
from .Nodes import *
from collections.abc import Iterable
import math
import numpy as np


class Graph(nx.Graph):
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

    def __getitem__(self, id_key):
        # get node by id
        return self.id2node[id_key]

    def add_victim(self, victim_type, id=None, name=None, location=None):
        """ Register a victim node to graph and append the corresponding lists

        :param id: the victim id, if id not give, the method will auto generate one
        :param name: the name of the Victim such as Jason. (Default None)
        :param victim_type: Must be one of [Yellow, Green, Dead, Safe]
        :param location: location of the victim, tuple of x,z coordinate
        :return: the victim node constructed
        """
        assert id is None or isinstance(id, str)
        assert name is None or isinstance(name, str)
        assert isinstance(victim_type, VictimType)
        assert location is None or isinstance(location, tuple) and len(location) == 2 \
               and all(isinstance(l, float) or isinstance(l, int) for l in location)

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

        node = VictimNode(node_id, name, victim_type, location)
        self.victimType2list[victim_type].append(node)
        self.victim_list.append(node)
        self.nodes_list.append(node)
        self.id2node[node_id] = node

        self.add_node(node)

        return node

    def add_portal(self, connected_room_ids, id=None, name=None, location=None):
        """ Add portal (pair)

        :param id: the portal id, if id not give, the method will auto generate one
        :param name: name of the portal, if any
        :param connected_room: the room that the portal is connected to
        :param location: location of the portal, tuple of x,z coordinate
        :return: the created portal node
        """
        assert id is None or isinstance(id, str)
        assert name is None or isinstance(name, str)
        assert location is None or isinstance(location, tuple) and len(location) == 2 \
               and all(isinstance(l, float) or isinstance(l, int) for l in location)
        assert isinstance(connected_room_ids, tuple) and all(isinstance(r, str) for r in connected_room_ids)

        node_id = id if id is not None else "P" + str(len(self.portal_list))

        node_id_1 = node_id + "-" + connected_room_ids[0]
        node_id_2 = node_id + "-" + connected_room_ids[1]

        node_1 = PortalNode(node_id_1, name, location)
        node_2 = PortalNode(node_id_2, name, location)
        node_1.link_portal(node_2)
        node_2.link_portal(node_1)
        self.add_edge(node_1, node_2, weight=1)

        self.portal_list.append((node_1, node_2))
        self.nodes_list.append(node_1)
        self.nodes_list.append(node_2)
        self.id2node[node_id_1] = node_1
        self.id2node[node_id_2] = node_2

        return node_1, node_2


    def add_room(self, id=None, name=None, location=None, victims=None):
        """ Add Room Node
        :param id: the room id, if id not give, the method will auto generate one
        :param name: name of the room, if any
        :param location: location of the center of the room, tuple of x,z coordinate
        :param victims: None or a list of victim id string
        :return: the created room node
        """
        assert id is None or isinstance(id, str)
        assert name is None or isinstance(name, str)
        assert victims is None or isinstance(victims, list) and \
               all(v is None or isinstance(v, str) for v in victims)
        assert location is None or isinstance(location, tuple) and len(location) == 2 \
               and all(isinstance(l, float) or isinstance(l, int) for l in location)

        node_id = id if id is not None else "R" + str(len(self.room_list))
        node = RoomNode(node_id, name, location, victims)

        self.room_list.append(node)
        self.nodes_list.append(node)
        self.id2node[node_id] = node

        return node

    def link_victims_in_room(self, room, list_of_victim_id):
        """ The First Linkage Function to run
        Make a fully connected sub-graph of room nodes and victims node inside that room

        :param room: the room Node
        :param list_of_victim_id: the list of victim ids inside the room
        :return: the room node
        """
        assert isinstance(room, RoomNode)
        assert isinstance(list_of_victim_id, list) and all(isinstance(v, str) for v in list_of_victim_id)

        for v_id in list_of_victim_id:
            victim = self.id2node[v_id]
            self.add_edge(room, victim, weight=self.euclidean_distances(room.loc, victim.loc))

        for i in range(len(list_of_victim_id)):
            for j in range(i+1, len(list_of_victim_id)):
                victim_1 = self.id2node[list_of_victim_id[i]]
                victim_2 = self.id2node[list_of_victim_id[j]]
                self.add_edge(victim_1, victim_2, weight=self.euclidean_distances(victim_1.loc, victim_2.loc))

        return room

    def connect_portal_to_rooms(self, portal_tuple):
        """ The second Linkage Function to run
        Connect the portal to the two rooms it is adjacent to
        :param portal_tuple: the two portals indicate two sides of the door
        """
        assert isinstance(portal_tuple, tuple) and len(portal_tuple) == 2 and \
               all(isinstance(p, PortalNode) for p in portal_tuple)

        portal_1, portal_2 = portal_tuple

        # connecting portal with the two adjacent rooms
        room_1 = self.id2node[portal_1.get_connected_room_id()]
        room_2 = self.id2node[portal_2.get_connected_room_id()]
        self.add_edge(portal_1, room_1, weight=self.euclidean_distances(room_1.loc, portal_1.loc))
        self.add_edge(portal_2, room_2, weight=self.euclidean_distances(room_2.loc, portal_2.loc))

        # connecting portal with all the victims in side the adjacent room
        for v_id in room_1.victim_list:
            victim = self.id2node[v_id]
            self.add_edge(portal_1, victim, weight=self.euclidean_distances(room_1.loc, victim.loc))

        for v_id in room_2.victim_list:
            victim = self.id2node[v_id]
            self.add_edge(portal_2, victim, weight=self.euclidean_distances(room_2.loc, victim.loc))

    def connected_portals_to_portals(self, portal_tuple):
        """ The third Linkage Function to run
        Connect the portal to portals that is connected with the room it is adjacent to
        :param portal_tuple: the two portals indicate two sides of the door
        """
        assert isinstance(portal_tuple, tuple) and len(portal_tuple) == 2 and \
               all(isinstance(p, PortalNode) for p in portal_tuple)

        portal_1, portal_2 = portal_tuple

        # Get the two adjacent rooms
        room_1 = self.id2node[portal_1.get_connected_room_id()]
        room_2 = self.id2node[portal_2.get_connected_room_id()]

        for n in self.get_neighbors(room_1):
            if n.type == NodeType.Portal and n != portal_1 and not self.has_edge(n, portal_1):
                self.add_edge(portal_1, n, weight=self.euclidean_distances(portal_1.loc, n.loc))

        for n in self.get_neighbors(room_2):
            if n.type == NodeType.Portal and n != portal_2 and not self.has_edge(n, portal_2):
                self.add_edge(portal_2, n, weight=self.euclidean_distances(portal_2.loc, n.loc))

    def get_neighbors(self, node):
        return self.neighbors(node)

    def get_edge_cost(self, node1, node2):
        return self.get_edge_data(node1, node2)["weight"]

    def close_all_portal(self):
        for portal_pair in self.portal_list:
            portal_pair[0].close_portal()

    def open_all_portal(self):
        for portal_pair in self.portal_list:
            portal_pair[0].open_portal()

    def kill_all_yellow_victims(self):
        for yellow_victim in self.yellow_victim_list:
            yellow_victim.yellow_death()
        self.dead_victim_list += self.yellow_victim_list
        self.yellow_victim_list = []

    def has_yellow_victim_in(self, room):
        assert isinstance(room, RoomNode)
        return any(self.id2node[n].victim_type == VictimType.Yellow for n in room.victim_list)

    def has_green_victim_in(self, room):
        assert isinstance(room, RoomNode)
        return any(self.id2node[n].victim_type == VictimType.Green for n in room.victim_list)

    def better_layout(self, with_spring=False, portal_sep=1.5):
        layout_dict = dict()
        fix_node = list()
        for node in self.nodes_list:
            loc = np.array([node.loc[0], node.loc[1]],dtype=np.float64)
            layout_dict[node] = loc

        if with_spring:
            for node in self.nodes_list:
                fix = True
                for nei in self.neighbors(node):
                    if self.euclidean_distances(node.loc, nei.loc) < 2:
                        fix = False
                if fix:
                    fix_node.append(node)

        # separate overlapping portal
        for portal_pair in self.portal_list:
            portal_1, portal_2 = portal_pair
            room_1 = self.id2node[portal_1.get_connected_room_id()]
            room_2 = self.id2node[portal_2.get_connected_room_id()]
            dist_1 = self.euclidean_distances(portal_1.loc, room_1.loc)
            dist_2 = self.euclidean_distances(portal_2.loc, room_2.loc)
            if dist_1 > dist_2:
                pos_1 = self.shift_distance(portal_sep, portal_1.loc, room_1.loc)
                layout_dict[portal_1] = np.array(pos_1)
            else:
                pos_2 = self.shift_distance(portal_sep, portal_2.loc, room_2.loc)
                layout_dict[portal_2] = np.array(pos_2)


        return layout_dict, fix_node

    def better_color(self):
        color_map = []
        for node in self:
            if node.type == NodeType.Victim:
                if node.victim_type == VictimType.Green:
                    color_map.append('limegreen')
                if node.victim_type == VictimType.Yellow:
                    color_map.append('yellow')
                if node.victim_type == VictimType.Dead:
                    color_map.append('tomato')
                if node.victim_type == VictimType.Safe:
                    color_map.append('silver')
            if node.type == NodeType.Portal:
                color_map.append('goldenrod')
            if node.type == NodeType.Room:
                color_map.append('lightskyblue')
        return color_map

    def flip_z(self, pos):
        # flip the graph along z-axis
        assert isinstance(pos, dict)
        for p in pos:
            pos[p][0] *= -1
        return pos

    def flip_x(self, pos):
        # flip the graph along x-axis
        assert isinstance(pos, dict)
        for p in pos:
            pos[p][1] *= -1
        return pos

    def clockwise90(self, pos):
        # rotate the graph clock-wise 90 degrees
        assert isinstance(pos, dict)
        for p in pos:
            pos[p][0], pos[p][1] = pos[p][1], -pos[p][0]
        return pos




    @staticmethod
    def euclidean_distances(pos1, pos2):
        assert isinstance(pos1, tuple) and isinstance(pos2, tuple)
        return max(1, math.ceil(math.sqrt((pos2[0] - pos1[0]) ** 2 + (pos2[1] - pos1[1]) ** 2)))

    def shift_distance(self, shift, pos1, pos2):
        """ Shift pos1 the distance "shift" to pos2
        :param shift: the distance want to shift
        :return: pos1 after shift
        """
        assert isinstance(shift, int) or isinstance(shift, float)
        assert isinstance(pos1, tuple) and isinstance(pos2, tuple)

        dist = self.euclidean_distances(pos1, pos2)
        if shift >= dist:
            return pos1

        ratio = shift / dist
        new_x = pos1[0] + ratio * (pos2[0] - pos1[0])
        new_z = pos1[1] + ratio * (pos2[1] - pos1[1])
        return new_x, new_z

