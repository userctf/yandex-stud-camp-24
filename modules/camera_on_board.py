import math
from module import BaseModule
from base_camera import BaseCamera, Prediction, ObjectType

from time import sleep
from inference import get_model
import numpy
import cv2
import socket
from enum import Enum
from typing import Tuple, List
from move import Move
from arm import Arm
import cProfile

NEURAL_MODEL = "robot_camera_detector/1"


class CameraOnBoard(BaseCamera):
    CONFIDENCE = 0.5

    def __init__(self, onboard_stream_url: str, neural_model_id: str, api_key: str):
        super().__init__(onboard_stream_url, neural_model_id, api_key)

    def get_len_to(self, game_object: ObjectType) -> (int, int):
        frame = self.get_photo()
        items = self.get_objects(frame, game_object)
        if len(items) == 0:
            return -1, -1
        most_relevant = items[0]
        coords = most_relevant.get_coords()
        obj_x = (coords[0][0] + coords[1][0]) // 2
        obj_y = coords[1][1]
        return self.__get_mm_by_coords(obj_x, obj_y)

    def __get_mm_by_coords(self, x: int, y: int) -> (int, int):
        m = self.__get_projection_matrix()
        proj_x, proj_y = self.__find_projection_coord(x, y, m)
        return self.__convert_coord_to_mm(proj_x, proj_y)

    def __convert_coord_to_mm(self, x: int, y: int) -> tuple[int, int]:
        # coords with respect to (0, 0) coord of arm
        x -= 600
        y = 2000 - y
        mm = 1
        pxl = 3
        return int(x * mm / pxl) + 73, int(y * mm / pxl) + 123

    def __get_projection_matrix(self) -> numpy.array:
        # precalced (see algo in git ml/robot_projection.py)
        transform_matrix = numpy.array([[1.05195863e+01,  1.27854429e+01, -2.73849594e+03],
                                        [1.94315457e-01,  6.44723966e+01, -7.95234016e+03],
                                        [-3.05200625e-05,  2.16211055e-02,  1.00000000e+00]])

        return transform_matrix

    def __find_projection_coord(self, x_src: int, y_src: int, proj_matrix: numpy.array) -> tuple[int, int]:
        x_dst = int((proj_matrix[0][0] * x_src + proj_matrix[0][1] * y_src + proj_matrix[0][2]) /
                    (proj_matrix[2][0] * x_src + proj_matrix[2][1] * y_src + proj_matrix[2][2]))
        y_dst = int((proj_matrix[1][0] * x_src + proj_matrix[1][1] * y_src + proj_matrix[1][2]) /
                    (proj_matrix[2][0] * x_src + proj_matrix[2][1] * y_src + proj_matrix[2][2]))
        return x_dst, y_dst


if __name__ == "__main__":
    host = "192.168.2.106"
    port = 2055

    # Создаем сокет
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"Соединение с {host}:{port}")

    # Устанавливаем соединение
    s.connect((host, port))
    S = CameraOnBoard("http://192.168.101.143:8080/?action=stream", NEURAL_MODEL, "uGu8WU7fJgR8qflCGaqP")
    S.test_cob(s.dup())
    
    s.close()
