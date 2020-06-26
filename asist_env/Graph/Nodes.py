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

    def __str__(self):
        return self.id if self.name is None else self.id + "_" + self.name


class PortalNode(Node):
    """
        portal Node id has format PID-RID (Portal ID - Room ID)
        for example,
    """
    def __init__(self, id, name, linked_portal_id, location):
        assert linked_portal_id is None or isinstance(linked_portal_id, str)
        super(Node, self).__init__(id, name)
        self.type = NodeType.Portal
        self.linked_portal_id = linked_portal_id
        self.loc = location

    def get_connected_room_id(self):
        return self.id.split("-")[1]

class VictimNode(Node):
    def __init__(self, id, name, victim_type, location):
        assert isinstance(victim_type, VictimType)
        super(Node, self).__init__(id, name)
        self.type = NodeType.Victim
        self.victim_type = victim_type
        self.loc = location


class RoomNode(Node):
    def __init__(self, id, name, location):
        super(Node, self).__init__(id, name)
        self.type = NodeType.Room
        self.loc = location

