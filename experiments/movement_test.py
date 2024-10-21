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

path = [(0, 90), (90, 90), (90, 0), (0, 0)]

move.move_along_path(path)








s.close()
print("Соединение закрыто")
