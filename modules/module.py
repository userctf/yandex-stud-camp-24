import socket
import time


class BaseModule:
    def __init__(self, s: socket.socket):
        self.socket = s
        pass

    def _send(self, message: bytearray, sleep_time: float):
        self.socket.sendall(message)
        time.sleep(sleep_time)
