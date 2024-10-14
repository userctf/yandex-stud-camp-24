import socket
import time
from copy import deepcopy
from time import sleep

host = "192.168.2.106"

port = 2055

# Создаем сокет
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print(f"Соединение с {host}:{port}")

# Устанавливаем соединение
def send_command(command):
    s.connect((host, port))
    try:
        s.sendall(command)
        data = s.recv(1024)
        s.close()
    except socket.error as e:
        print(f"Ошибка сокета: {e}")
        s.close()
        return False
    return data

command = b"\xff\x42\x00\x00\xff"
for i in range (100):
    res = send_command(command)
    if i % 5 == 0:
        print(res)
# Закрываем соединение

print("Соединение закрыто")
