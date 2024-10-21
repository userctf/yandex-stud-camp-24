from enum import Enum


class GameStartState(Enum):
    HORIZONTAL = 0
    VERTICAL = 1
    INNER_START_LIKE = 2
    INNER_COUNTER_START_LIKE = 3
    OUTER_START_LIKE = 5
    OUTER_COUNTER_START_LIKE = 6
    UNKNOWN = -1


class GameObjectType(Enum):
    CUBE = 0
    BALL = 1
    ANY_ROBOT = 4
    GREEN_BASE = 5
    BTN_GREEN_ORANGE = 6
    BTN_PINK_BLUE = 7
    RED_BASE = 8
    OUR_ROBOT = 9
    BAD_ROBOT = 10
    UNKNOWN = -1

class ObjectType(Enum):
    CUBE = 0
    BALL = 1  # it is detecting only by on board cam
    BASKET = 2  # it is detecting only by on board cam
    BUTTONS = 3  # it is detecting only by on board cam
    ROBOT = 4
    GREEN_BASE = 5
    BTN_G_O = 6
    BTN_P_B = 7
    UNKNOWN = -1

    def __lt__(self, other):
        if isinstance(other, ObjectType):
            return self.value < other.value
        return NotImplemented
