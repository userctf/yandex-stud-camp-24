import socket
import time


class BaseModule:
    RECV_LEN = 1024
    BEEP_MESSAGE = bytearray([255, 65, 1, 1, 255])
    
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
        
    def _get_response(self) -> bytes:
        try:
            data = self.s.recv(self.RECV_LEN)
            if not data:
                print(f"Данные от сокета не пришли: {e}")
                
            return data
        except socket.error as e:
            print(f"Ошибка сокета: {e}")
            