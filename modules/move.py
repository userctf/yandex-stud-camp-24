import time
import socket
from module import BaseModule

SLEEP_TIME = 0
BASE_MESSAGE = bytearray([255, 0, 0, 0, 255])
TIME_TO_TURN_360 = 2.3
TIME_TO_GO_100 = 4


class Move(BaseModule):
    def __init__(self, s: socket.socket):
        super().__init__(s.dup())

    def _send(self, message: bytearray, sleep_time=SLEEP_TIME):
        super()._send(message, sleep_time)

    def stop(self):
        msg = BASE_MESSAGE.copy()
        self._send(msg)
    
    def forward(self):
        msg = BASE_MESSAGE.copy()
        msg[2] = 1
        self._send(msg)

    def back(self):
        msg = BASE_MESSAGE.copy()
        msg[2] = 2
        self._send(msg)

    def left(self):
        msg = BASE_MESSAGE.copy()
        msg[2] = 3
        self._send(msg)

    def right(self):
        msg = BASE_MESSAGE.copy()
        msg[2] = 4
        self._send(msg)

    def go_forward(self, duration):
        if (0 < duration and duration < 2.55):
            msg = BASE_MESSAGE.copy()
            msg[1] = 68
            msg[2] = int(duration * 100)
            self._send(msg)
        else:
            print('duration must be from 0 to 2.54')

    def go_back(self, duration):
        if (0 < duration and duration < 2.55):
            msg = BASE_MESSAGE.copy()
            msg[1] = 69
            msg[2] = int(duration * 100)
            self._send(msg)
        else:
            print('duration must be from 0 to 2.54')
    
    def turn_right(self, duration):
        if (0 < duration and duration < 2.55):
                msg = BASE_MESSAGE.copy()
                msg[1] = 72
                msg[2] = int(duration * 100)
                self._send(msg)
        else:
            print('duration must be from 0 to 2.54')

    def turn_left(self, duration):
        if (0 < duration and duration < 2.55):
            msg = BASE_MESSAGE.copy()
            msg[1] = 71
            msg[2] = int(duration * 100)
            self._send(msg)
        else:
            print('duration must be from 0 to 2.54')

    

    
        