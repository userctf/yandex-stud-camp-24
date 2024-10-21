import time
import socket
import math
import numpy as np
from scipy.interpolate import interp1d
from module import BaseModule
from enum import Enum

SLEEP_TIME = 0
BASE_MESSAGE = bytearray([255, 0, 0, 0, 255])

DISTS = [0, 8, 12, 20, 39, 59, 77, 98]
TIMES_DIST = [0, 0.2, 0.3, 0.5, 1, 1.5, 2, 2.54]

ANGLES = [0, 5, 10, 15, 20, 30, 45, 60, 90, 120, 135, 180]
TIMES_RIGHT = [0, 0.07, 0.12, 0.16, 0.2, 0.27, 0.36, 0.45, 0.64, 0.8, 0.88, 1.15]
TIMES_LEFT = [0, 0.07, 0.12, 0.16, 0.2, 0.26, 0.37, 0.47, 0.67, 0.86, 0.94, 1.18]

class Dir(Enum):
    FORWARD = 68
    BACK = 69
    RIGHT = 72
    LEFT = 71

STOP_MOVING_RESPONSE = 'STOP_MOVING_RESPONSE'


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

    def set_speed(self, l_speed : int, r_speed: int):
        msg = BASE_MESSAGE.copy()
        msg[1] = 2

        msg[2] = 1
        msg[3] = r_speed
        self._send(msg)

        msg[2] = 2
        msg[3] = l_speed
        self._send(msg)



    # 0 < duration in seconds < 2.55
    def _move(self, direction : Dir, duration : float, emergency_stop : bool = True):
        if (0 < duration and duration < 2.55):
            time_moving = 0
            msg = BASE_MESSAGE.copy()
            msg[1] = direction.value
            msg[2] = int(duration * 100)
            msg[3] = emergency_stop
            self._send(msg)
            while True:
                response = self._get_response()
                if not response:
                    print('No response for > socket.timeout seconds')
                    break
                response_data = response.decode('utf-8').split('; ')
                if response_data[0] == STOP_MOVING_RESPONSE:
                    time_moving = float(response_data[1])
                    print(f'Got stop moving response after {time_moving} seconds moving')
                    break
                
                time.sleep(0.01)

            # update robot's state
            if direction == Dir.FORWARD:
                dist = self._time_to_dist(TIMES_DIST, DISTS, time_moving)
                self.__x_cord += dist * math.sin(math.radians(self.__angle))
                self.__y_cord += dist * math.cos(math.radians(self.__angle))
            elif direction == Dir.BACK:
                dist = self._time_to_dist(TIMES_DIST, DISTS, time_moving)
                self.__x_cord -= dist * math.sin(math.radians(self.__angle))
                self.__y_cord -= dist * math.cos(math.radians(self.__angle))
            elif direction == Dir.RIGHT:
                angle = self._time_to_angle(TIMES_RIGHT, ANGLES, time_moving)
                self.__angle = (self.__angle + angle) % 360
            elif direction == Dir.LEFT:
                angle = self._time_to_angle(TIMES_LEFT, ANGLES, time_moving)
                self.__angle = (self.__angle - angle + 360) % 360

            time.sleep(0.3)
        else:
            print('duration must be from 0 to 2.54')


    @staticmethod
    def _dist_to_time(dists, times, sm):
        piecewise_func = interp1d(dists, times, bounds_error=False, fill_value="extrapolate")
        return piecewise_func(sm)
    
    @staticmethod
    def _angle_to_time(angles, times, deg):
        piecewise_func = interp1d(angles, times, bounds_error=False, fill_value="extrapolate")
        return piecewise_func(deg)
    
    @staticmethod
    def _time_to_dist(times, dists, sec):
        piecewise_func = interp1d(times, dists, bounds_error=False, fill_value="extrapolate")
        return piecewise_func(sec)
    
    @staticmethod
    def _time_to_angle(times, angles, sec):
        piecewise_func = interp1d(times, angles, bounds_error=False, fill_value="extrapolate")
        return piecewise_func(sec)
    

    # -115 <= dist <= 115
    def go_sm(self, dist, emergency_stop : bool = True):
        duration = self._dist_to_time(DISTS, TIMES_DIST, abs(dist))
        if dist > 0:
            self._move(Dir.FORWARD, duration, emergency_stop)
        else:
            self._move(Dir.BACK, duration)

    # -360 <= deg <= 360
    def turn_deg(self, angle):
        # calculate the shortest way
        if angle > 180:
            angle = angle - 360
        elif angle < -180:
            angle = 360 + angle

        if angle > 0:
            duration = self._angle_to_time(ANGLES, TIMES_RIGHT, abs(angle))
            self._move(Dir.RIGHT, duration)
        else:
            duration = self._angle_to_time(ANGLES, TIMES_LEFT, abs(angle))
            self._move(Dir.LEFT, duration)

    # returns 0 - 360 angle between vector{x, y} and Oy
    @staticmethod
    def _calculate_clockwise_vector_angle(x, y):
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

    def move_to_point(self, x_dest : int, y_dest : int, stop_before_target=True):
            new_angle = self._calculate_new_angle(x_dest, y_dest)
            dist = self._calculate_dist_to_move(x_dest, y_dest)
            if stop_before_target:
                dist = dist // 2

            # print(f'Сейчас я в ({self.__x_cord}, {self.__y_cord})')
            # print(f'Направляюсь в ({x_dest}, {y_dest})')
            # print(f'Хочу повернуться на {new_angle - self.__angle} градусов')
            # print(f'И проехать на {dist} см')
            # print()
            # time.sleep(2)

            # turn to the destination
            if (new_angle != self.__angle):
                self.turn_deg(new_angle - self.__angle)

            # move to the destination
            while dist > 0:
                self.go_sm(min(dist, 95))
                dist -= min(dist, 95)

    def update_state(self, x: float, y: float, angle: float):
        HEIGHT = 321
        self.__x_cord = x
        self.__y_cord = HEIGHT - y

        diff = (angle - self.__angle + 360) % 360
        diff = min(diff, 360 - diff)
        if diff < 90:
            self.__angle = angle
        else:
            self.__angle = 180 - angle
