import math
import socket
import time
import cv2

from arm import Arm
from move import Move
from enum import Enum
from camera_on_board import CameraOnBoard
from base_camera import ObjectType
from game_map import GameMap
from top_camera import TopCamera
from sensors import Sensors


# Camera on board parameters
ON_BOARD_CAMERA_URL = "http://192.168.2.106:8080/?action=stream"
ON_BOARD_NEURAL_MODEL = "robot_camera_detector/1"
ON_BOARD_API_KEY = "uGu8WU7fJgR8qflCGaqP"
# Top board_camera parameters
TOP_CAMERA_URL = "rtsp://Admin:rtf123@192.168.2.250:554/1"
TOP_CAMERA_NEURAL_MODEL = 'detecting_objects-ygnzn/1'
TOP_CAMERA_API_KEY = "d6bnjs5HORwCF1APwuBX"


class GameTasks(Enum):
    FIND_AND_GRAB_FIRST_CUBE = 0
    FIND_AND_GRAB_SECOND_CUBE = 1
    FIND_AND_GRAB_BALL = 2
    DELIVER_FIRST_CUBE_TO_BASKET = 3
    DELIVER_SECOND_TO_BASKET = 4
    DELIVER_BALL_TO_BASKET = 5
    PRESS_FIRST_BUTTON = 6
    PRESS_SECOND_BUTTON = 7
    RETURN_TO_BASE = 8
    UNKNOWN = -1


class GameTasksType(Enum):
    NOT_STARTED = 0
    IN_PROCESS = 1
    COMPLETED = 2
    ERROR = -1


game_tasks = {
    GameTasks.FIND_AND_GRAB_FIRST_CUBE: GameTasksType.NOT_STARTED,
    GameTasks.FIND_AND_GRAB_SECOND_CUBE: GameTasksType.NOT_STARTED,
    GameTasks.FIND_AND_GRAB_BALL: GameTasksType.NOT_STARTED,
    GameTasks.DELIVER_FIRST_CUBE_TO_BASKET: GameTasksType.NOT_STARTED,
    GameTasks.DELIVER_SECOND_TO_BASKET: GameTasksType.NOT_STARTED,
    GameTasks.DELIVER_BALL_TO_BASKET: GameTasksType.NOT_STARTED,
    GameTasks.PRESS_FIRST_BUTTON: GameTasksType.NOT_STARTED,
    GameTasks.PRESS_SECOND_BUTTON: GameTasksType.NOT_STARTED,
    GameTasks.RETURN_TO_BASE: GameTasksType.NOT_STARTED,
    GameTasks.UNKNOWN: GameTasksType.NOT_STARTED
}


class Robot:
    def __init__(self, s: socket.socket):
        self.arm = Arm(s)
        self.move = Move(s)
        self.top_camera = TopCamera(TOP_CAMERA_URL, TOP_CAMERA_NEURAL_MODEL, TOP_CAMERA_API_KEY)
        self.map = GameMap(self.top_camera)
        self.board_camera = CameraOnBoard(ON_BOARD_CAMERA_URL, ON_BOARD_NEURAL_MODEL, ON_BOARD_API_KEY)
        # Need to add sensors

    def __get_angle_to_object(self, x_obj: int, y_obj: int) -> int:
        x_center = 35
        y_center = -140
        length = math.sqrt((x_obj - x_center) ** 2 + (y_obj - y_center) ** 2)
        gamma = math.asin(abs(x_center) / length)
        alpha = math.atan2(x_obj - x_center, y_obj - y_center)
        rotate_angle = alpha + gamma
        return int(rotate_angle * 180 / math.pi + 0.5)

    def __find_object(self, game_object: ObjectType) -> bool:
        for i in range(1, 5):
            self.move.go_sm(-10) # Надо проверить, что может ехать назад
            x, y = self.board_camera.get_len_to(game_object)
            if (x, y) != (-1, -1):
                return True

            angle = 15
            if i == 1 or i == 3:
                angle = 20
            self.move.turn_deg((-1)**i * (angle * i))
            # print(f'Here: {i}')

            x, y = self.board_camera.get_len_to(game_object)
            if (x, y) != (-1, -1):
                return True
        return False

    def check_taking_object(self, game_object: ObjectType) -> bool:
        x, y = self.board_camera.get_len_to(game_object)
        if (x, y) == (-1, -1):
            return True
        return False

    def find_and_grab_object(self, game_object: ObjectType) -> bool:
        while True:
            x, y = self.board_camera.get_len_to(game_object)
            # print(f"Distance im mm: x{x}, y{y}")

            if (x, y) == (-1, -1):
                if not self.__find_object(game_object):
                    return False

            # Too close: robot will not be able to grab the object
            if y < 120:  # MAGIC NUMBER
                self.move.go_sm(-4)
                # time.sleep(1)
                continue

            # Let's grab it
            if y < 220 and abs(x) < 40:  # MAGIC NUMBER
                self.arm.grab(y + 30)
                time.sleep(0.5)
                return self.check_taking_object(game_object)

            # Turn towards object
            angle = self.__get_angle_to_object(x_obj=x, y_obj=y)
            self.move.turn_deg(angle * 0.5)

            # Recalc dist after turn
            x, y = self.board_camera.get_len_to(ObjectType.CUBE)

            # Move towards object
            self.move.go_sm(y // 20)

    def throw_in_basket(self) -> bool:
        game_object = ObjectType.BASKET
        while True:
            x, y = self.board_camera.get_len_to(game_object)
            # print(f'Distance to object: x {x}, y {y}')
            if (x, y) == (-1, -1):
                if not self.__find_object(game_object):
                    return False

            angle = self.__get_angle_to_object(x, y)
            self.move.turn_deg(angle)

            x_new, y_new = self.board_camera.get_len_to(game_object)

            if y_new <= 160:
                if x_new <= 30:
                    self.move.go_sm((y_new - 90) // 10)
                    self.arm.release()
                    return True
                else:
                    angle = self.__get_angle_to_object(x_new, y_new)
                    self.move.turn_deg(angle)

            self.move.go_sm(min((y_new - 150) // 10, y_new // 20))

    def move_along_path(self, game_object):
        path = self.map.get_path(game_object)
        self.move.move_along_path(path)


if __name__ == '__main__':
    host = "192.168.2.106"
    port = 2055

    # Создаем сокет
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"Соединение с {host}:{port}")

    # Устанавливаем соединение
    s.connect((host, port))

    robot = Robot(s)
    print(robot.find_and_grab_object(ObjectType.CUBE))
    print(robot.throw_in_basket())
