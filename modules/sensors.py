from module import BaseModule

import cv2
import requests
import numpy
import socket
from typing import List



class Sensors(BaseModule):
    BASE_MESSAGE = bytearray([0xff, 0x42, 0, 0, 0xff])
    
    def __init__(self, s: socket.socket):
        super().__init__(s.dup())


    def _send(self, message: bytearray):
        super()._send(message, 0)
        
    def _send_and_get(self, cmd: bytearray) -> str:
        self._send(cmd)
        data = self._get_response().decode('utf-8')
        print("[DEBUG]", data)
        return data
    
    
    # sensor poll
    def get_IR_up(self) -> List[bool]:
        cmd = self.BASE_MESSAGE.copy()
        cmd[2] = 0x00
        return [i == "1" for i in self._send_and_get(cmd).split('\n')]
    
    def get_ultrasonic_dist(self) -> float:
        cmd = self.BASE_MESSAGE.copy()
        cmd[2] = 0x02
        return float(self._send_and_get(cmd))

        
if __name__ == "__main__":
    host = "192.168.2.106"

    port = 2055

    # Создаем сокет
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"Соединение с {host}:{port}")

    # Устанавливаем соединение
    s.connect((host, port))
    S = Sensors(s.dup())
    print(S.get_IR_up())
