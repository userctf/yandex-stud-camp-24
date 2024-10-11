import socket
import time

host = "192.168.2.106"

port = 2055

# Создаем сокет
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print(f"Соединение с {host}:{port}")

# Устанавливаем соединение
s.connect((host, port))


def send_command(command: bytearray) -> bool:
    try:
        print(f"Отправка команды: {command}")
        # Отправляем команду
        s.sendall(command)

        # Добавляем небольшой задержку между отправками команд
        time.sleep(0.5)

        return True
    except socket.error as e:
        print(f"Ошибка сокета: {e}")
        return False


# Первая команда
commands_prepare_grab = [
    bytearray([255, 1, 4, 40, 255]),
    bytearray([255, 1, 3, 85, 255]),
    bytearray([255, 1, 1, 143, 255]),
    bytearray([255, 1, 2, 41, 255]),
    bytearray([255, 1, 1, 137, 255]),
]
time.sleep(4)
commands_make_grab = [
    bytearray([255, 1, 4, 86, 255]),
    bytearray([255, 1, 2, 83, 255]),
    bytearray([255, 1, 1, 143, 255]),
    bytearray([255, 1, 3, 170, 255]),
    bytearray([255, 1, 1, 155, 255]),
    bytearray([255, 1, 2, 29, 255]),
]
commands_default = [
    bytearray([255, 1, 2, 103, 255]),
    bytearray([255, 1, 1, 123, 255]),
    bytearray([255, 1, 2, 123, 255]),
    bytearray([255, 1, 1, 143, 255]),
]

for command in commands_prepare_grab:
    result = send_command(command)
    if not result:
        print("An error occurred")

for command in commands_make_grab:
    result = send_command(command)
    if not result:
        print("An error occurred")

for command in commands_default:
    result = send_command(command)

# Закрываем соединение
s.close()
print("Соединение закрыто")
