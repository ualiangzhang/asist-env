from abc import ABC, abstractmethod
from enum import Enum

class NodeType(Enum):
    Portal = 0
    Victim = 1
    Room = 2

class VictimType(Enum):
    Yellow = 0
    Green = 1
    Dead = 2
    Safe = 3

class Node(ABC):
    def __init__(self, name):
        self.name = name
        self.visited_count = 0

    def __str__(self):
        return self.name


class PortalNode(Node):
    def __init__(self, name, room_connected, paired_other):
        super(Node, self).__init__(name)
        self.type = NodeType.Portal
        self.room_connected = room_connected
        self.paired_other = paired_other

class VictimNode(Node):
    def __init__(self, name, victim_type):
        assert isinstance(victim_type, VictimType)

        super(Node, self).__init__(name)
        self.type = NodeType.Victim
        self.victim_type = victim_type

class RoomNode(Node):
    def __init__(self, name):
        super(Node, self).__init__(name)
        self.type = NodeType.Room

