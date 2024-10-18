import sys
import os
import keyboard

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../modules')))
from move import Move

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

# x_path = [0, -90, -140]
# y_path = [90, 130, 220]

# move.move_along_path(x_path, y_path)

move.go_sm(50)
time.sleep(1)
move.turn_deg(80)
time.sleep(1)
move.go_sm(75)


s.close()
print("Соединение закрыто")
