import graph
import pandas as pd
import numpy as np
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
    def __init__(self, portal_data, room_data, victim_data, start_node_id):
        self.graph = MapParser.parse_map_data(portal_data, room_data, victim_data)
        # self.graph_copy = self.graph.copy()
        self.start_node_id = start_node_id
        self.curr_pos = self.graph[start_node_id]
        self.prev_pos = None
        self.total_cost = 0
        self.score = 0
        self.positive_reward_multiplier = 10
        self.victim_data = victim_data
        # TODO: Add Memory (Graph)

    def reset(self):
        self.curr_pos = self.graph[self.start_node_id]
        self.graph.reset()
        # self.graph = self.graph_copy.copy()
        self.total_cost = 0
        self.score = 0
        self.prev_pos = None
        # return self.get_observation()
        return self.get_unorganized_observation()

    def get_victim_list_size(self):
        return len(self.graph.victim_list)

    def step(self, action):
        """ The global view
        :param performance: 0: navigate, 1: enter, 2: triage
        :param action_node: the index of the node for your performance
        :return: (observation, reward)
        """
        # assert performance in [0, 1, 2]
        raise NotImplementedError
        performance, action_node_idx = action

        reward = 0
        action_node = self.graph.nodes_list[action_node_idx]

        triage_set = set()
        navigation_set = set()
        portal_enter_set = set()
        for n in self.graph.neighbors(self.curr_pos):
            if n.type == graph.NodeType.Portal:
                if self.curr_pos.type == graph.NodeType.Portal and \
                        n.is_same_portal(self.curr_pos):
                    portal_enter_set.add(n)
                else:
                    navigation_set.add(n)
            elif n.type == graph.NodeType.Victim:
                triage_set.add(n)
            elif n.type == graph.NodeType.Room:
                navigation_set.add(n)

        valid_action = True
        if performance == 0 and action_node not in navigation_set:
            valid_action = False
        if performance == 1 and action_node not in portal_enter_set:
            valid_action = False
        if performance == 2 and action_node not in triage_set:
            valid_action = False

        if not valid_action:
            reward -= 100
            # print("ha")
        else:
            # print(action)
            edge_cost = self.graph.get_edge_cost(self.curr_pos, action_node)
            self.prev_pos = self.curr_pos
            self.curr_pos = action_node
            reward -= edge_cost
            self.total_cost += edge_cost
            if action_node.type == graph.NodeType.Victim:
                triage_cost, triage_score = self.graph.triage(action_node)
                reward -= triage_cost
                self.total_cost += triage_cost
                self.score += triage_score
                reward += triage_score * self.positive_reward_multiplier

        done = False
        if self.graph.no_more_victims() or self.total_cost > 1000:
            done = True
        return self.get_observation(), reward, done

    def step_unorganized(self, action):
        action_node = self.graph.nodes_list[action]
        reward = 0
        if not any(action_node.id == n.id for n in self.graph.neighbors(self.curr_pos)):
            reward -= 100
        else:
            # print(action)
            edge_cost = self.graph.get_edge_cost(self.curr_pos, action_node)
            self.prev_pos = self.curr_pos
            self.curr_pos = action_node
            reward -= edge_cost
            self.total_cost += edge_cost
            if action_node.type == graph.NodeType.Victim:
                triage_cost, triage_score = self.graph.triage(action_node)
                reward -= triage_cost
                self.total_cost += triage_cost
                self.score += triage_score
                reward += triage_score * self.positive_reward_multiplier

        done = False
        if self.graph.no_more_victims() or self.total_cost > 1000:
            done = True
        return self.get_observation(), reward, done

    def step_old(self, action):
        """ The global view
        :param performance: 0: navigate, 1: enter, 2: triage
        :param action_node: the index of the node for your performance
        :return: (observation, reward)
        """
        # assert performance in [0, 1, 2]

        performance, action_node_idx = action

        reward = 0
        action_node = self.graph.nodes_list[action_node_idx]

        triage_set = set()
        navigation_set = set()
        portal_enter_set = set()
        for n in self.graph.neighbors(self.curr_pos):
            if n.type == graph.NodeType.Portal:
                if self.curr_pos.type == graph.NodeType.Portal and \
                        n.is_same_portal(self.curr_pos):
                    portal_enter_set.add(n)
                else:
                    navigation_set.add(n)
            elif n.type == graph.NodeType.Victim:
                triage_set.add(n)
            elif n.type == graph.NodeType.Room:
                navigation_set.add(n)

        valid_action = True
        if performance == 0 and action_node not in navigation_set:
            valid_action = False
        if performance == 1 and action_node not in portal_enter_set:
            valid_action = False
        if performance == 2 and action_node not in triage_set:
            valid_action = False

        if not valid_action:
            reward -= 100
            # print("ha")
        else:
            # print(action)
            edge_cost = self.graph.get_edge_cost(self.curr_pos, action_node)
            self.prev_pos = self.curr_pos
            self.curr_pos = action_node
            reward -= edge_cost
            self.total_cost += edge_cost
            if action_node.type == graph.NodeType.Victim:
                triage_cost, triage_score = self.graph.triage(action_node)
                reward -= triage_cost
                self.total_cost += triage_cost
                self.score += triage_score
                reward += triage_score * self.positive_reward_multiplier

        done = False
        if self.graph.no_more_victims() or self.total_cost > 1000:
            done = True
        return self.get_observation(), reward, done

    def step_for_console_play(self, action):
        action_cost = self.graph.get_edge_cost(self.curr_pos, action)
        action_score = 0
        if action.type == graph.NodeType.Victim:
            triage_cost, triage_score = action.triage()
            action_cost += triage_cost
            action_score += triage_score
        self.total_cost += action_cost
        self.score += action_score
        self.prev_pos = self.curr_pos
        self.curr_pos = action

    def get_observation(self):
        """ Observation is an array of the following:
        [room_observed, portal_observed, victim_observed, device_info]
        all nodes are listed and set to 0 initially, if the agent is in neighbor to
        any of those nodes, the value is set to 1, for victims, types are indicated
        as (1, 2, 3, 4) being (green, yellow, safe, dead) respectively
        lets say the map has one portal_pair, two rooms, and one yellow victim
        [start, r1 | p0-start, p0-r1 | vy1] + [device] could be [0, 1, 1, 0, 1] + [0]
        :return: the observation array
        """
        room_observation = np.zeros(len(self.graph.room_list))
        portal_observation = np.zeros(len(self.graph.portal_list) * 2)
        victim_observation = np.zeros(len(self.graph.victim_list))

        for n in self.graph.get_neighbors(self.curr_pos):
            if n.type == graph.NodeType.Room:
                room_observation[self.graph.room_list.index(n)] = 1
            if n.type == graph.NodeType.Portal:
                # need to find the exact portal index since the portal list stores tuples of portals
                idx = None
                for pl_idx, pt in enumerate(self.graph.portal_list):
                    if n.id == pt[0].id:
                        idx = pl_idx * 2
                        break
                    elif n.id == pt[1].id:
                        idx = pl_idx * 2 + 1
                        break
                portal_observation[idx] = 1
            if n.type == graph.NodeType.Victim:
                victim_observation[self.graph.victim_list.index(n)] = 1 + n.victim_type.value
        device_info = np.array([self.get_device_info()])
        return np.concatenate([room_observation, portal_observation, victim_observation, device_info])

    def get_unorganized_observation(self):
        node_observation = np.zeros(len(self.graph.nodes_list))
        for n in self.graph.get_neighbors(self.curr_pos):
            if n.type == graph.NodeType.Room or n.type == graph.NodeType.Portal:
                node_observation[self.graph.nodes_list.index(n)] = 1
            if n.type == graph.NodeType.Victim:
                node_observation[self.graph.nodes_list.index(n)] = 1 + n.victim_type.value
        device_info = np.array([self.get_device_info()])
        return np.concatenate([node_observation, device_info])

    def get_observation_debug(self):
        """ Debug observation, to be deleted
        :return: the observation array with value and node id as tuple
        """
        room_observation = [(0, haha.id) for haha in self.graph.room_list]
        portal_observation = []
        for haha in self.graph.portal_list:
            portal_observation.append((0, haha[0].id))
            portal_observation.append((0, haha[1].id))
        victim_observation = [(0, haha.id) for haha in self.graph.victim_list]
        for n in self.graph.get_neighbors(self.curr_pos):
            if n.type == graph.NodeType.Room:
                room_observation[self.graph.room_list.index(n)] = (1, n.id)
            if n.type == graph.NodeType.Portal:
                # need to find the exact portal index since the portal list stores tuples of portals
                idx = None
                for pl_idx, pt in enumerate(self.graph.portal_list):
                    if n.id == pt[0].id:
                        idx = pl_idx * 2
                        break
                    elif n.id == pt[1].id:
                        idx = pl_idx * 2 + 1
                        break
                portal_observation[idx] = (1, n.id)
            if n.type == graph.NodeType.Victim:
                victim_observation[self.graph.victim_list.index(n)] = (1 + n.victim_type.value, n.id)
        device_info = np.array([self.get_device_info()])
        return room_observation + portal_observation + victim_observation

    def get_observation_old(self):
        """ (Discarded) Observation is an array of the following:
        [cur_pos, device_info, victim_1_state, victim_2_state, victim_3_state, ...]
        :return: the above array
        """
        cur_pos = self.graph.nodes_list.index(self.curr_pos)
        device_info = self.get_device_info()
        victim_states = [n.victim_type.value for n in self.graph.victim_list]
        return tuple(np.array([cur_pos] + [device_info] + victim_states))

    def get_action_space_for_console_play(self):
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
        # Nothing: 0,  Green: 1, Yellow: 2,
        if self.curr_pos.type == graph.NodeType.Portal:
            connected_room = self.graph.id2node[self.curr_pos.linked_portal.get_connected_room_id()]
            if self.graph.has_yellow_victim_in(connected_room):
                return 2
            elif self.graph.has_green_victim_in(connected_room):
                return 1
        return 0

    def get_device_info_for_console_play(self):
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
            print("Total Reward:", str(self.score))
            print("Device Info:", self.get_device_info_for_console_play())
            print()

            print(self.get_observation())

            # for idx, obs in enumerate(self.get_observation()):
            #     print(str(obs), end=" ")
            #     if idx %5 == 0:
            #         print()

            action_space, action_space_str = self.get_action_space_for_console_play()
            print("Possible Actions:")
            print("\n".join(str(idx) + ": " + act_str for idx, act_str in enumerate(action_space_str)))
            act = input("Choose an Action: ")
            if act == "q":
                break
            print()
            chosen_action = action_space[int(act)]
            self.step_for_console_play(chosen_action)

if __name__ == '__main__':
    data_folder = Path("data")

    portals_csv = data_folder / "sparky_portals.csv"
    rooms_csv = data_folder / "sparky_rooms.csv"
    victims_csv = data_folder / "sparky_victims.csv"

    portal_data = pd.read_csv(portals_csv)
    room_data = pd.read_csv(rooms_csv)
    victim_data = pd.read_csv(victims_csv)

    env = AsistEnv(portal_data, room_data, victim_data, "as")
    env.console_play()
    # print(env.get_observation())
