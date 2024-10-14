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

print(dir(s))
print()

arm = Arm(s.dup())

arm.open_hand()
arm.close_hand()
time.sleep(1)
arm.rotate_hand_horizontal()
arm.set_arm(0, 300)
arm.set_arm(300, 110)
time.sleep(3)
arm.set_arm(0, 300)


s.close()
print("Соединение закрыто")
