from abc import ABC, abstractmethod
from enum import Enum

class NodeType(Enum):
    Portal = 0
    Victim = 1
    Room = 2

class VictimType(Enum):
    Green = 0
    Yellow = 1
    Safe = 2
    Dead = 3

class Node(ABC):
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.visited_count = 0

    @abstractmethod
    def __str__(self):
        pass

class PortalNode(Node):
    def __init__(self, name):
        super(Node, self).__init__(name)
        self.type = NodeType.Portal
        self.connected_room_id = None
        self.portal_counterpart = None

    def __str__(self):
        pass

class VictimNode(Node):
    def __init__(self, id, name, victim_type):
        assert isinstance(victim_type, VictimType)
        super(Node, self).__init__(id, name)
        self.type = NodeType.Victim
        self.victim_type = victim_type

    def __str__(self):
        return self.id if self.name is None else self.id + "_" + self.name

class RoomNode(Node):
    def __init__(self, name):
        super(Node, self).__init__(name)
        self.type = NodeType.Room

