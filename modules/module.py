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