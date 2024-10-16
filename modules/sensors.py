from module import BaseModule

import cv2
import requests
import numpy
import socket
from typing import List



class Sensors(BaseModule):
    BASE_MESSAGE = bytearray([255, 42, 0, 0, 255])
    
    def __init__(self, s: socket.socket, onboard_stream_url: str, upper_stream_url: str):
        super().__init__(s.dup())
        self.onboard_stream_url = onboard_stream_url
        self.upper_stream_url = upper_stream_url

    def _send(self, message: bytearray):
        super()._send(message, 0)
        
    def _send_and_get(self, cmd: bytearray) -> str:
        self._send(cmd)
        return self._get_respone().decode('utf-8')
    
    
    # sensor poll
    def get_IR_up(self) -> List[bool]:
        cmd = BASE_MESSAGE.copy()
        cmd[2] = 0x00
        return [bool(i) for i in _send_and_get(cmd).split('\n')]
        
    def get_IR_down(self) -> List[bool]:
        cmd = BASE_MESSAGE.copy()
        cmd[2] = 0x01
        return [bool(i) for i in _send_and_get(cmd).split('\n')]
    
    def get_ultrasonic_dist(self) -> float:
        cmd = BASE_MESSAGE.copy()
        cmd[2] = 0x02
        return float(_send_and_get(cmd))
    
    # get photo from stream
    def get_photo(self, is_onboard_cap = True) -> numpy.ndarray:
        url = self.onboard_stream_url if is_onboard_cap else self.upper_stream_url
        jpg = self.__read_jpg_from_stream(url)
        img = cv2.imdecode(numpy.frombuffer(jpg, dtype=numpy.uint8), cv2.IMREAD_COLOR)
        return img
                    
    def __read_jpg_from_stream(self, url: str) -> bytes:
        stream = requests.get(url, stream=True)
        read_bytes = bytes()
        for chunk in stream.iter_content(chunk_size=1024):
            read_bytes += chunk
            a = read_bytes.find(b'\xff\xd8') # jpg start
            b = read_bytes.find(b'\xff\xd9') # jpg end
            if a != -1 and b != -1:
                jpg = read_bytes[a:b+2]
                # read_bytes = read_bytes[b+2:]
                return jpg
        
        stream.close()
        
   
