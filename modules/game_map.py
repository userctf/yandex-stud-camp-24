from typing import List

from zxingcpp import Position

from modules.base_camera import ObjectType
from top_camera import TopCamera
from enum import Enum


class GameObjectPosition(Enum):
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


game_objects = {
    GameObjectType.CUBE : [None, None],
    GameObjectType.BALL : None,
    GameObjectType.GREEN_BASE : None,
    GameObjectType.RED_BASE: None,
    GameObjectType.OUR_ROBOT: None,
    GameObjectType.BAD_ROBOT: None,
    GameObjectType.BTN_PINK_BLUE: None,
    GameObjectType.BTN_GREEN_ORANGE: None,
}


class GameObject:
    def __init__(self, ):
        self.x
        self.y
        self.w
        self.h
        self.last_seen
        self.type

    def get_center(self) -> Position:
        pass

    def get_approach_points(self) -> List[Position]:
        pass


class GameMap:
    def __init__(self, top_camera: TopCamera):
        self.top_camera = top_camera
        self.game_objects = game_objects.copy()
        self.inner_boards = GameObjectPosition.UNKNOWN
        self.outer_boards = GameObjectPosition.UNKNOWN

    def _set_frame_limits(self):
        # вызывается при инициализации. Нужен для перевода в координаты и обратно
        pass

    def _frame_to_map_position(self, first: Position, other: Position):
        # Using limits from _set_frame_limits. Can't be made static
        pass

    def _find_all_game_objects(self):
        # инициализация. Работает пока не заполним 2 куба, обоих роботов, обе базы, обе кнопки
        pass

    def get_robot_position(self, frame, predictions) -> Position:
        pass
