import socket
import time
import sys
import os

host = "192.168.2.106"

port = 2055

# Создаем сокет
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print(f"Соединение с {host}:{port}")

# Устанавливаем соединение
s.connect((host, port))

def run_commands(commands: list[bytearray]):
    for command in commands:
        result = send_command(command)
        if not result:
            print("An error occurred")


def send_command(command: bytearray) -> bool:
    try:
        print(f"Отправка команды: {command}")
        # Отправляем команду
        s.sendall(command)

        time.sleep(0.5)

        return True
    except socket.error as e:
        print(f"Ошибка сокета: {e}")
        return False

GREEN = 0x00
RED = 0x01
VIOLET = 0x02
command_color = bytearray([0xff, 0x43,GREEN, 0x70, 0xff])
send_command(command_color)
