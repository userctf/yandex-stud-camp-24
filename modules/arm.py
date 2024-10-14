import math
import socket
import time
from pyexpat.errors import messages

from modules.module import BaseModule

SLEEP_TIME = 0.5

BASE_MESSAGE = bytearray([255, 1, 0, 90, 255])
BEEP_MESSAGE = bytearray([255, 65, 1, 1, 255])


class Arm(BaseModule):
    def __init__(self, s: socket.socket):
        super().__init__(s)

    def _send(self, message: bytearray, sleep_time=SLEEP_TIME):
        super()._send(message, sleep_time)

    def _calculate_angles(self, length: int, height: int) -> tuple[int, int]:
        l1 = 95
        l2 = 160
        radius = l1 + l2

        height -= 50
        height = max(height, -50)
        length = max(length, 65)

        gamma = math.atan2(height, length)
        length = min(length, int(radius * math.cos(gamma)))
        if height < 0:
            height = max(height, int(radius * math.sin(gamma)))
        else:
            height = min(height, int(radius * math.sin(gamma)))

        Q1 = math.atan(height / length) + math.acos(
            (l1 ** 2 + length ** 2 + height ** 2 - l2 ** 2) / (2 * l1 * (length ** 2 + height ** 2) ** 0.5))
        Q2 = math.pi - math.acos((l1 ** 2 + l2 ** 2 - length ** 2 - height ** 2) / (2 * l1 * l2))

        first = min(int(81 + Q1 * 180 / math.pi), 170)
        second = min(int(180 - Q2 * 180 / math.pi), 170)

        return first, second


def _make_message(self, servo: int, angle: int):
    if servo not in (1, 2, 3, 4):
        return BEEP_MESSAGE
    if angle > 170 or angle < 15:
        return BEEP_MESSAGE
    message = BASE_MESSAGE.copy()
    message[1] = servo
    message[2] = angle
    return message


def close_hand(self, ball: bool = False):
    if ball:
        message = self._make_message(4, 82)
    else:
        message = self._make_message(4, 77)
    self._send(message)


def open_hand(self):
    self._send(self._make_message(4, 53))


def rotate_hand_vertical(self):
    self._send(self._make_message(3, 170))


def rotate_hand_horizontal(self):
    self._send(self._make_message(3, 90))


def set_arm(self, length: int, height: int):
    first, second = self._calculate_angles(length, height)
    print(f"{length, height}: Calculated angles are f{first} and {second}")
    self._send(self._make_message(1, first))
    self._send(self._make_message(2, second))
