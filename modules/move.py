import time
import socket
import math
import numpy as np
from scipy.interpolate import interp1d
from module import BaseModule

SLEEP_TIME = 0
BASE_MESSAGE = bytearray([255, 0, 0, 0, 255])

DISTS_FORWARD = [0, 2, 10, 23, 47, 92, 115]
TIMES_FORWARD = [0, 0.1, 0.25, 0.5, 1, 2, 2.54]

ANGLES_RIGHT = [0, 10, 20, 30, 45, 90, 120, 180]
TIMES_RIGHT = [0, 0.13, 0.2, 0.27, 0.3, 0.6, 0.75, 1.05]


class Move(BaseModule):
    def __init__(self, s: socket.socket, x_cord : int = 0, y_cord : int = 0, angle : int = 0):
        super().__init__(s.dup())
        self.__x_cord = x_cord
        self.__y_cord = y_cord
        self.__angle = angle

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

    def _dist_to_time(self, dists, times, sm):
        piecewise_func = interp1d(dists, times, bounds_error=False, fill_value="extrapolate")
        return piecewise_func(sm)
        
    def _angle_to_time(self, angles, times, deg):
        piecewise_func = interp1d(angles, times, bounds_error=False, fill_value="extrapolate")
        return piecewise_func(deg)
    

    # -115 <= dist <= 115
    def go_sm(self, dist):
        if dist > 0:
            self.go_forward(self._dist_to_time(DISTS_FORWARD, TIMES_FORWARD, dist))
        else:
            self.go_back(self._dist_to_time(DISTS_FORWARD, TIMES_FORWARD, -dist))

    # -360 <= deg <= 360
    def turn_deg(self, angle):
        if angle > 180:
            angle = angle - 360
        elif angle < -180:
            angle = 360 + angle
        if angle > 0:
            self.turn_right(self._angle_to_time(ANGLES_RIGHT, TIMES_RIGHT, angle))
        else:
            self.turn_left(self._angle_to_time(ANGLES_RIGHT, TIMES_RIGHT, -angle))

    # returns 0 - 360 angle between vector {x, y} and Oy
    def _calculate_clockwise_vector_angle(self, x, y):
        if (x==0 and y ==0):
            raise ValueError("The vector cannot have zero length")
        angle_rad = math.acos(y / math.sqrt(x**2+y**2))
        angle_deg = math.degrees(angle_rad)
        angle_clockwise = angle_deg if x >= 0 else 360 - angle_deg
        return angle_clockwise
    
    def _calculate_new_angle(self, x_dest, y_dest):
        return self._calculate_clockwise_vector_angle(x_dest - self.__x_cord, y_dest - self.__y_cord)
    
    def _calculate_dist_to_move(self, dest_x, y_dest):
        return math.sqrt((self.__x_cord - dest_x)**2 + (self.__y_cord - y_dest)**2)

    def move_along_path(self, x_path : list[int], y_path : list[int]):
        # iterate over nodes
        for x_dest, y_dest in zip(x_path, y_path):
            # skip if position has not changed
            if (self.__x_cord == x_dest and self.__y_cord == y_dest):
                continue
                
            new_angle = self._calculate_new_angle(x_dest, y_dest)
            dist = self._calculate_dist_to_move(x_dest, y_dest)

            # print(f'Сейчас я в ({self.__x_cord}, {self.__y_cord})')
            # print(f'Направляюсь в ({x_dest}, {y_dest})')
            # print(f'Хочу повернуться на {new_angle - self.__angle} градусов')
            # print(f'И проехать на {dist} см')
            # print()
            # time.sleep(2)

            # turn to next node
            if (new_angle != self.__angle):
                self.turn_deg(new_angle - self.__angle)
                time.sleep(2)

            # move to next node
            while dist > 0:
                self.go_sm(min(dist, 110))
                time.sleep(3)
                dist -= min(dist, 110)
            
            

            #update our state
            self.__angle = new_angle
            self.__x_cord = x_dest
            self.__y_cord = y_dest
