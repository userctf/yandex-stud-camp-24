import math
import socket
import time
from typing import List, Tuple
import cv2

from arm import Arm
from camera_mock import CameraMock
from utils.position import Position
from move import Move
from enum import Enum
from camera_on_board import CameraOnBoard
from utils.enums import ObjectType, GameObjectType
from utils.gameobject import GameObject
from game_map import GameMap
from top_camera import TopCamera
from sensors import Sensors


# Camera on board parameters
ON_BOARD_CAMERA_URL = "http://192.168.101.143:8080/?action=stream"
ON_BOARD_NEURAL_MODEL = "robot_camera_detector/1"
ON_BOARD_API_KEY = "uGu8WU7fJgR8qflCGaqP"
# Top board_camera parameters
TOP_CAMERA_URL = "rtsp://Admin:rtf123@192.168.2.251:554/1"
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
    def __init__(self, s: socket.socket, is_left: bool = True, color: str = "red"):
        self.arm = Arm(s)
        
        self.top_camera = CameraMock(TOP_CAMERA_URL, TOP_CAMERA_NEURAL_MODEL, TOP_CAMERA_API_KEY)
        self.map = GameMap(self.top_camera, is_left=is_left, color=color)
        self.board_camera = CameraOnBoard(ON_BOARD_CAMERA_URL, ON_BOARD_NEURAL_MODEL, ON_BOARD_API_KEY)

        x = self.map.get_our_robot().get_center().x
        y = self.map.get_our_robot().get_center().y
        # left bottom
        angle = self.map.get_our_robot().get_center().angle
        # right top
        if y < 150: # Magic number Approx half of the image
            angle = (180 + angle) % 360

        self.move = Move(s, x, y, angle)

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
                    self.move.go_sm((y_new - 90) // 10, False)
                    self.arm.release()
                    return True
                else:
                    angle = self.__get_angle_to_object(x_new, y_new)
                    self.move.turn_deg(angle)

            self.move.go_sm(min((y_new - 150) // 10, y_new // 20), False)

    def move_along_path(self, game_object: GameObjectType):
        path = self.map.find_path_to(game_object)
        for x, y in path:
            self.move.move_to_point(x, y, stop_before_target=((x, y) == path[-1]))
            time.sleep(1)
            # self.map.find_all_game_objects()
            # map_robot = self.map.get_our_robot()
            # if time.time() - map_robot.last_seen < 0.3:
            #     self.move.update_state(*map_robot.position)
            # path = self.map.find_path_to(game_object)



if __name__ == '__main__':
    host = "192.168.101.143"
    port = 2055

    # Создаем сокет
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"Соединение с {host}:{port}")

    # Устанавливаем соединение
    s.connect((host, port))

    robot = Robot(s, is_left=True, color="green")
    robot.map.find_all_game_objects()
    print("Дошли до куба")
    print(robot.map.get_our_robot())
    robot.move.update_state(*(robot.map.get_our_robot().position))
    print("Started moving along path...............")
    robot.move_along_path(GameObjectType.CUBE)
    print("Just ended moving along path...............")
    print("Дошли до куба")
    robot.find_and_grab_object(ObjectType.CUBE)
    print("Vzyali")
    robot.move_along_path(GameObjectType.RED_BASE)

    robot.throw_in_basket()