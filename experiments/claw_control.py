import socket
import time
from modules.arm import Arm

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


arm = Arm(s.dup())

# arm.set_arm(10, 300)
# arm.rotate_hand_horizontal()
# arm.close_hand()
# arm.open_hand()
# time.sleep(5)
# arm.set_arm(10, 300)

# while True:
#     arm.set_arm(150, 100)
#     arm.set_arm(150, 200)
arm.grab(100)
arm.default()





s.close()
print("Соединение закрыто")
