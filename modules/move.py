import time
import socket
from module import BaseModule

SLEEP_TIME = 0
BASE_MESSAGE = bytearray([255, 0, 0, 0, 255])
TIME_TO_TURN_360 = 2.3
TIME_TO_GO_100 = 5


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

    def turn(self, angle):
        if (angle > 0):
            self.right()
        else:
            self.left()
        time.sleep(TIME_TO_TURN_360 / 360 * abs(angle))
        self.stop()

    def go(self, distance):
        if (distance > 0):
            self.forward()
        else:
            self.back()
        time.sleep(TIME_TO_GO_100 / 100 * abs(distance))
        self.stop()
        