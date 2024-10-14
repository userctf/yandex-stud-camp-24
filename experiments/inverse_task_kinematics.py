import math
import socket
import time


def inverse_task(x: int, y: int) -> tuple[int, int]:
    # в миллиметрах
    l1 = 95
    l2 = 160
    y -= 50
    Q1 = math.atan(y / x) + math.acos((l1**2 + x**2 + y**2 - l2**2) / (2 * l1 * (x**2 + y**2)**0.5))
    Q2 = math.pi - math.acos((l1**2 + l2**2 - x**2 - y**2) / (2 * l1 * l2))
    alpha = int(81 + Q1 * 180 / math.pi)
    betta = int(180 - Q2 * 180 / math.pi)
    print(alpha, betta)
    return alpha, betta


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

        # Добавляем небольшой задержку между отправками команд
        time.sleep(0.5)

        return True
    except socket.error as e:
        print(f"Ошибка сокета: {e}")
        return False


alpha, betta = inverse_task(210, 100)



commands_prepare_grab = [
    bytearray([255, 1, 4, 60, 255]),
    bytearray([255, 1, 3, 85, 255]),
    bytearray([255, 1, 1, 143, 255]),
    bytearray([255, 1, 2, 41, 255]),
    bytearray([255, 1, 1, 137, 255]),
]

commands_forward_hand = [
    bytearray([255, 1, 2, betta, 255]),
    bytearray([255, 1, 1, alpha, 255]),
]

commands_make_grab = [
    bytearray([255, 1, 4, 77, 255]),
    bytearray([255, 1, 2, 83, 255]),
    bytearray([255, 1, 1, 143, 255]),
    bytearray([255, 1, 3, 170, 255]),
    bytearray([255, 1, 1, 155, 255]),
    bytearray([255, 1, 2, 29, 255]),
]

# run_commands(commands_prepare_grab)
run_commands(commands_forward_hand)
# run_commands(commands_make_grab)

# Закрываем соединение
s.close()
print("Соединение закрыто")

