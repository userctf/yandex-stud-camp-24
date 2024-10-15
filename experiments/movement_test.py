import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../modules')))
from move import Move

import socket
import time
#from modules.move import Move

host = "192.168.2.106"

port = 2055

# Создаем сокет
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print(f"Соединение с {host}:{port}")

# Устанавливаем соединение
s.connect((host, port))

move = Move(s.dup())

# move.right()
# time.sleep(2.3)
# print('start moving')
# move.stop()

move.go(10)


s.close()
print("Соединение закрыто")
