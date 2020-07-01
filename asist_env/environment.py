import graph
import pandas as pd
from pathlib import Path

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
            # is_open = row['isOpen'] == "TRUE"
            # g.add_portal(tuple(eval(row["connections"])), is_open, id=row["id"], location=eval(row["loc"]))
            g.add_portal(tuple(eval(row["connections"])), id=row["id"], location=eval(row["loc"]))

        for room in g.room_list:
            g.link_victims_in_room(room, room.victim_list)

        for portal_pair in g.portal_list:
            g.connect_portal_to_rooms(portal_pair)

        for portal_pair in g.portal_list:
            g.connected_portals_to_portals(portal_pair)

        return g

class AsistEnvRandGen:
    def __init__(self):
        pass

class AsistEnv:
    def __init__(self, portal_data, room_data, victim_data):
        self.graph = MapParser.parse_map_data(portal_data, room_data, victim_data)
        self.curr_pos = self.graph["Start"]
        self.prev_pos = None
        self.total_cost = 0
        self.reward = 0
        # TODO: Add Memory (Graph)

    def reset(self):
        pass

    def step(self, action):
        action_cost = self.graph.get_edge_cost(self.curr_pos, action)
        action_reward = 0
        if action.type == graph.NodeType.Victim:
            triage_cost, triage_reward = action.triage()
            action_cost += triage_cost
            action_reward += triage_reward
        self.total_cost += action_cost
        self.reward += action_reward
        self.prev_pos = self.curr_pos
        self.curr_pos = action

    def get_action_space(self):
        victim_list = []
        portal_navigation_list = []
        portal_enter_list = []
        room_list = []

        victim_list_str = []
        portal_navigation_list_str = []
        portal_enter_list_str = []
        room_list_str = []
        for n in self.graph.neighbors(self.curr_pos):
            if n.type == graph.NodeType.Portal:
                if self.curr_pos.type == graph.NodeType.Portal and \
                        n.is_same_portal(self.curr_pos):
                    portal_enter_list.append(n)
                    act_str = "Enter Portal {} to Portal {}".format(str(self.curr_pos), str(n))
                    if n == self.prev_pos:
                        act_str += " [Go Back]"
                    portal_enter_list_str.append(act_str)
                else:
                    portal_navigation_list.append(n)
                    act_str = "Navigate to Portal {}".format(str(n))
                    if n == self.prev_pos:
                        act_str += " [Go Back]"
                    portal_navigation_list_str.append(act_str)
            elif n.type == graph.NodeType.Victim:
                victim_list.append(n)
                act_str = "Triage Victim {} ({})".format(str(n), n.get_type_str())
                if n == self.prev_pos:
                    act_str += " [Go Back]"
                victim_list_str.append(act_str)
            elif n.type == graph.NodeType.Room:
                room_list.append(n)
                act_str = "Enter Room Center {}".format(str(n))
                if n == self.prev_pos:
                    act_str += " [Go Back]"
                room_list_str.append(act_str)
        action_space = portal_navigation_list + portal_enter_list + victim_list + room_list
        action_space_str = portal_navigation_list_str + portal_enter_list_str + victim_list_str + room_list_str

        return action_space, action_space_str

    def get_device_info(self):
        if self.curr_pos.type == graph.NodeType.Portal:
            connected_room = self.graph.id2node[self.curr_pos.linked_portal.get_connected_room_id()]
            if self.graph.has_yellow_victim_in(connected_room):
                return "Beep-Beep"
            elif self.graph.has_green_victim_in(connected_room):
                return "Beep"
        return "Nothing"

    def console_play(self):
        while True:
            print("============================================\n")
            print("Your Current Position:", str(self.curr_pos))
            print("Your Previous Position:", str(self.prev_pos))
            print("Total Cost:", str(self.total_cost))
            print("Total Reward:", str(self.reward))
            print("Device Info:", self.get_device_info())
            print()

            action_space, action_space_str = self.get_action_space()
            print("Possible Actions:")
            print("\n".join(str(idx) + ": " + act_str for idx, act_str in enumerate(action_space_str)))
            act = input("Choose an Action: ")
            if act == "q":
                break
            print()
            chosen_action = action_space[int(act)]
            self.step(chosen_action)

if __name__ == '__main__':
    data_folder = Path("data")

    portals_csv = data_folder / "sparky_portals.csv"
    rooms_csv = data_folder / "sparky_rooms.csv"
    victims_csv = data_folder / "sparky_victims.csv"

    portal_data = pd.read_csv(portals_csv)
    room_data = pd.read_csv(rooms_csv)
    victim_data = pd.read_csv(victims_csv)

    env = AsistEnv(portal_data, room_data, victim_data)
    env.console_play()

