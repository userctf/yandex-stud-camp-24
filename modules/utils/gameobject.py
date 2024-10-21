import time
from typing import List, Tuple

from .position import Position
from .enums import GameObjectType


WIDTH = 421
HEIGHT = 321

CUBE_APPROACH = 30

class GameObject:
    def __init__(self, position: Position, size: Tuple[float, float], object_type: GameObjectType):
        self.position = position
        self.w = int(size[0])
        self.h = int(size[1])
        self.last_seen = time.time()
        self.type = object_type

    def get_center(self) -> Position:
        return self.position

    def get_approach_points(self) -> List[Position]:
        return [self.position]

    def __repr__(self):
        return f"{self.type} with center {self.position}. Last seen at {self.last_seen}"


class Base(GameObject):  # Это База
    def __init__(self, position: Position, size: Tuple[float, float], object_type: GameObjectType):
        super().__init__(position, size, object_type)

    def get_approach_points(self) -> List[Position]:
        vector_up = Position(0, self.h // 2)
        vector_down = Position(0, -1 * self.h // 2)
        vector_right = Position(self.w // 2, 0)
        vector_left = Position(-1 * self.w // 2, 0)

        if 130 <= self.position.x <= 270:
            if self.position.y <= 160:
                return [self.position + vector_left, self.position + vector_right,
                        self.position + vector_down]
            else:
                return [self.position + vector_left, self.position + vector_right,
                        self.position + vector_up]
        else:
            if self.position.x <= 200:
                return [self.position + vector_right, self.position + vector_up,
                        self.position + vector_down]
            else:
                return [self.position + vector_left, self.position + vector_up,
                        self.position + vector_down]


class Cube(GameObject):
    def get_approach_points(self) -> List[Position]:
        result = []
        if self.position.x < WIDTH // 2:
            result.append(self.position + Position(CUBE_APPROACH, 0))
        else:
            result.append(self.position + Position(-CUBE_APPROACH, 0))
        if self.position.y < HEIGHT // 2:
            result.append(self.position + Position(0, CUBE_APPROACH))
        else:
            result.append(self.position + Position(0, -CUBE_APPROACH))
        print(self, result)
        return result
