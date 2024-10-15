import socket
import time

class BaseModule:
    def __init__(self, s: socket.socket):
        self.socket = s
        pass

    def _send(self, message: bytearray, sleep_time: float):
        try:
            self.socket.sendall(message)
        except socket.error as e:
            print(f"Ошибка сокета: {e}")
        time.sleep(sleep_time)