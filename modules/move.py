import time
import socket
import numpy as np
from scipy.interpolate import interp1d
from module import BaseModule

SLEEP_TIME = 0
BASE_MESSAGE = bytearray([255, 0, 0, 0, 255])

DISTS_FORWARD = [2, 10, 23, 47, 92, 115]
TIMES_FORWARD = [0.1, 0.25, 0.5, 1, 2, 2.54]

ANGLES_RIGHT = [10, 20, 30, 45, 90, 120, 180]
TIMES_RIGHT = [0.13, 0.2, 0.27, 0.3, 0.6, 0.75, 1.05]


def dist_to_time(dists, times, sm):
    piecewise_func = interp1d(dists, times, bounds_error=False, fill_value="extrapolate")
    return piecewise_func(sm)
        
def angle_to_time(angles, times, deg):
    piecewise_func = interp1d(angles, times, bounds_error=False, fill_value="extrapolate")
    return piecewise_func(deg)


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

    # def set_speed(self, left, right):
    #     msg = BASE_MESSAGE.copy()
    #     msg[1] = 2
    #     msg[2] = 1
    #     msg[2] = 50
    #     self._send(msg)
    #     msg[1] = 2
    #     msg[2] = 2
    #     msg[2] = 100
    #     self._send(msg)
    

    # -115 <= dist <= 115
    def go_sm(self, dist):
        if dist > 0:
            self.go_forward(dist_to_time(DISTS_FORWARD, TIMES_FORWARD, dist))
        else:
            self.go_back(dist_to_time(DISTS_FORWARD, TIMES_FORWARD, -dist))

    # -180 <= deg <= 180
    def turn_deg(self, angle):
        if angle > 0:
            self.turn_right(angle_to_time(ANGLES_RIGHT, TIMES_RIGHT, angle))
        else:
            self.turn_left(angle_to_time(ANGLES_RIGHT, TIMES_RIGHT, -angle))

