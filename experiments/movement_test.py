import sys
import os
import keyboard
from enum import Enum

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../modules')))
from move import Move
from arm import Arm


import socket
import time

host = "192.168.2.106"

port = 2055

# Создаем сокет
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print(f"Соединение с {host}:{port}")

# Устанавливаем соединение
s.connect((host, port))
s.settimeout(3)
move = Move(s.dup())
#arm = Arm(s.dup())

# x_path = [0, 90]
# y_path = [90, -100]

# move.move_along_path(x_path, y_path)

class Dir(Enum):
    FORWARD = 68
    BACK = 69
    RIGHT = 72
    LEFT = 71

move.set_speed(66, 62)

for i in range(3):
    move._move(Dir.LEFT, 0.86)







s.close()
print("Соединение закрыто")
