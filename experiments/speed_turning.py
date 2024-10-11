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

        # Добавляем небольшой задержку между отправками команд
        time.sleep(0)

        return True
    except socket.error as e:
        print(f"Ошибка сокета: {e}")
        return False

BASE_SPEED = 80
FAST_SPEED = 100

commands_turn_left= [
    bytearray([255, 2, 1, FAST_SPEED, 255]),
    bytearray([255, 2, 2, FAST_SPEED, 255]),

    bytearray([255, 0, 1, 0, 255]),
    "sleep 2.3",

    bytearray([255, 2, 1, BASE_SPEED, 255]),
    bytearray([255, 2, 2, BASE_SPEED // 3, 255]),
    "sleep 1.5",
    bytearray([255, 2, 1, BASE_SPEED, 255]),
    bytearray([255, 2, 2, BASE_SPEED, 255]),
]

commands_turn_right = deepcopy(commands_turn_left)
commands_turn_right[2][2] = 2
commands_turn_right[4][2] = 2

for command in commands_turn_left:
    if type(command) is str and "sleep" in command:
        print("sleeping")
        time.sleep(float(command.split()[1]))
        continue
    send_command(command)

# Закрываем соединение
s.close()
print("Соединение закрыто")
