from .Graph import *

class MapParser:
    def __init__(self):
        pass

    @classmethod
    def parse_map(cls, map_data):
        """ Given Map Data, construct a Graph
        :param map_data: map data file provided
        :return: the graph
        """
        return Graph()

class AsistEnvRandGen:
    def __init__(self):
        pass

class AsistEnv:
    def __init__(self):
        self.graph = MapParser.parse_map()

    def step(self):
        pass

    def action_space(self):
        pass

    def reset(self):
        pass