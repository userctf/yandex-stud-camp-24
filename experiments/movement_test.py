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


for i in range(6):
    #move.turn_deg(30)
    move.turn_right(0.27)
    time.sleep(1.5)

s.close()
print("Соединение закрыто")
