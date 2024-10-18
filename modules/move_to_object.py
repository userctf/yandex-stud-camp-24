import math
import os
import sys
import socket

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../modules')))
from move import Move
from isensors import ISensors, ObjectType
from arm import Arm


def rotate_to_object(x_obj: int, y_obj: int) -> int:
    # coord of rotate center of robot
    x_center = 35
    y_center = -140
    lenght = math.sqrt((x_obj - x_center)**2 + (y_obj - y_center)**2)
    gamma = math.asin(abs(x_center) / lenght)
    alpha = math.atan2(x_obj - x_center, y_obj - y_center)
    rotate_angle = alpha + gamma
    return int(rotate_angle * 180 / math.pi + 0.5)


def move_to_object(vehicle: Move, sensor: ISensors, arm: Arm):
    epsilon = 5 # degree

    while True:
        x_cube, y_cube = sensor.get_len_to(ObjectType.CUBE)
        print(x_cube, y_cube)

        if (x_cube, y_cube) == (-1, -1):
            # vehicle.go_sm(-20)
            print("No box found")
            break

        if -20 <= x_cube <= 20 and y_cube <= 230:
            arm.grab(y_cube + 20) # center of box
            break

        rotate_to_object_angle = rotate_to_object(x_cube, y_cube)
        vehicle.turn_deg(rotate_to_object_angle)

        x_cube_new, y_cube_new = sensor.get_len_to(ObjectType.CUBE)
        # length = y_cube_new - abs(x_cube_new / math.tan(epsilon))
        # print(length)

        # if length <= y_cube_new // 2:
        #     continue
        # else:
        vehicle.go_sm(y_cube_new // 20)


host = "192.168.2.106"

port = 2055

# Создаем сокет
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print(f"Соединение с {host}:{port}")

# Устанавливаем соединение
s.connect((host, port))
robot_arm = Arm(s)
robot_sensor = ISensors(s, "http://192.168.2.106:8080/?action=stream", None, "uGu8WU7fJgR8qflCGaqP")
robot_move = Move(s)

move_to_object(robot_move, robot_sensor, robot_arm)
# S.test()
# print("len to box:", self.get_len_to(ObjectType.CUBE))

s.close()
