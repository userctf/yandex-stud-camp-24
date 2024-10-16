import socket
import time




class BaseModule:
    def __init__(self, s: socket.socket):
        self.socket = s
        pass

    def _send(self, message: bytearray, sleep_time: float) -> bool:
        try:
            self.socket.sendall(message)
        except socket.error as e:
            print(f"Ошибка сокета: {e}")
            return False
        time.sleep(sleep_time)
        return True


    def __send_command(self, command: bytearray) -> bool:
        try:
            print(f"Отправка команды: {command}")
            # Отправляем команду
            self.socket.sendall(command)

            # Добавляем небольшой задержку между отправками команд
            time.sleep(0.5)

            return True
        except socket.error as e:
            print(f"Ошибка сокета: {e}")
            return False