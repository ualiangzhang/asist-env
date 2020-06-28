import graph
import pandas as pd

class MapParser:

    @classmethod
    def victim_type_str_to_type(cls, type_str):
        if type_str == "Green":
            return graph.VictimType.Green
        if type_str == "Gold":
            return graph.VictimType.Yellow

    @classmethod
    def parse_map_data(cls, portal_data, room_data, victim_data):
        """ Given Map Data, construct a Graph
        :param portal_data: pandas data-frame for portal_data
        :param room_data: pandas data-frame for room_data
        :param victim_data: pandas data-frame for victim_data
        :return: the graph
        """
        g = graph.Graph()
        for index, row in room_data.iterrows():
            g.add_room(id=row["id"], location=eval(row["loc"]), victims=eval(row["connections"]))

        for index, row in victim_data.iterrows():
            g.add_victim(cls.victim_type_str_to_type(row["type"]), id=row["id"], location=eval(row["loc"]))

        for index, row in portal_data.iterrows():
            g.add_portal(tuple(eval(row["connections"])), row["id"], location=eval(row["loc"]))

        for room in g.room_list:
            g.link_victims_in_room(room, room.victim_list)

        for portal_pair in g.portal_list:
            g.connect_portal_to_rooms(portal_pair)

        return g

class AsistEnvRandGen:
    def __init__(self):
        pass

class AsistEnv:
    def __init__(self):
        self.graph = MapParser.parse_map_data()
        self.curr_pos = graph["Start"]
        self.total_cost = 0
        self.reward = 0
        # TODO: Add Memory (Graph)

    def reset(self):
        pass

    def step(self):
        pass

    def get_action_space(self):
        choice_count = 0
        victim_list = []
        portal_list = []
        the_room = None
        for n in self.graph.neighbors(self.curr_pos):
            if n.type == graph.NodeType.Portal:
                portal_list.append(n)
            elif n.type == graph.NodeType.Victim:
                victim_list.append(n)
            elif n.type == graph.NodeType.Room:
                the_room = n



    def get_victims_in_room(self):
        pass

    def get_device_info(self):
        pass

    def console_play(self):
        while True:
            print("Your Current Position:", str(self.curr_pos))

            action_str = ""
            act = input("Choose Action:\n" + action_str)

