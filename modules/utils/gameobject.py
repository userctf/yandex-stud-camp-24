import time
from typing import List, Tuple
from utils.position import Position
from utils.enums import GameObjectType
class GameObject:
    def __init__(self, position: Position, size: Tuple[float, float], object_type: GameObjectType):
        self.position = position
        self.w = int(size[0])
        self.h = int(size[0])
        self.last_seen = time.time()
        self.type = object_type

    def get_center(self) -> Position:
        return self.position

    def get_approach_points(self) -> List[Position]:
        pass

    def __repr__(self):
        return f"{self.type} with center {self.position}. Last seen at {self.last_seen}"

