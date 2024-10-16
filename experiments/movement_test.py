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
move = Move(s.dup())

for i in range(8):
    move.turn_left(0.37)
    time.sleep(1)


s.close()
print("Соединение закрыто")
