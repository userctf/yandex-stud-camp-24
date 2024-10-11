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
s.connect((host, port))


def send_command(command):
    try:
        print(f"Отправка команды: {command}")
        # Отправляем команду
        s.sendall(command)

        while True:
            data = s.recv(1024)
            if not data:
                break
            print("recv: ", data)

            time.sleep(0.1)

    except socket.error as e:
        print(f"Ошибка сокета: {e}")
        return False

command = b"\xff\x42\x00\x00\xff"
send_command(command)
# Закрываем соединение
s.close()
print("Соединение закрыто")
