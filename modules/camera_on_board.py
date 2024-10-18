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

    def test_cob(self):
        # move = Move(s)
        while True:
            img = self.get_photo()
            p = self.predict(img)
            frame = self._write_on_img(img, p)

            cv2.imshow('Frame with Box', img)
            x, y = self.get_len_to(ObjectType.CUBE)
            print(f"Distance im mm: x{x}, y{y}")

            # if (x, y) == (-1, -1):
            #     # Try to find it
            #     #  TODO
            #     move.go_sm(-10)
            #     move.turn_deg(-10)
            #     continue

            # # Too close: robot will not be able to grab the object
            # if y < 120: # MAGIC NUMBER
            #     move.go_sm(-10)
            #     continue

            # # Let's grab it
            # if y < 220 and abs(x) < 40: # MAGIC NUMBER
            #     arm = Arm(s)
            #     arm.grab(y + 20)
            #     return

            # # Turn towards object
            # angle = self._get_angle_to_object(x_obj=x, y_obj=y)
            # move.turn_deg(angle)            

            # # Recalc dist after turn
            # x, y = self.get_len_to(ObjectType.CUBE)

            # # Move towards object
            # move.go_sm(y//20)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cv2.destroyAllWindows()

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
        mm = 105
        pxl = 305
        return int(x * mm / pxl) + 75, int(y * mm / pxl) + 110

    def __get_projection_matrix(self) -> numpy.array:
        transform_matrix = numpy.array([[7.11620049e+00, 8.68669211e+00, -1.70901081e+03],
                                        [-2.19522636e-01, 4.36212775e+01, -4.64586208e+03],
                                        [-1.94267820e-04, 1.47179361e-02, 1.00000000e+00]])
        return transform_matrix

    def __get_angle_to_object(self, x_obj: int, y_obj: int) -> int:
        x_center = 35
        y_center = -140
        length = math.sqrt((x_obj - x_center) ** 2 + (y_obj - y_center) ** 2)
        gamma = math.asin(abs(x_center) / length)
        alpha = math.atan2(x_obj - x_center, y_obj - y_center)
        rotate_angle = alpha + gamma
        return int(rotate_angle * 180 / math.pi + 0.5)

    def __find_projection_coord(self, x_src: int, y_src: int, proj_matrix: numpy.array) -> tuple[int, int]:
        x_dst = int((proj_matrix[0][0] * x_src + proj_matrix[0][1] * y_src + proj_matrix[0][2]) /
                    (proj_matrix[2][0] * x_src + proj_matrix[2][1] * y_src + proj_matrix[2][2]))
        y_dst = int((proj_matrix[1][0] * x_src + proj_matrix[1][1] * y_src + proj_matrix[1][2]) /
                    (proj_matrix[2][0] * x_src + proj_matrix[2][1] * y_src + proj_matrix[2][2]))
        return x_dst, y_dst


if __name__ == "__main__":
    S = CameraOnBoard("http://192.168.2.106:8080/?action=stream", NEURAL_MODEL, "uGu8WU7fJgR8qflCGaqP")
    S.test_cob()
