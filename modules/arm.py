import math
import socket
from modules.module import BaseModule

SLEEP_TIME = 0.4

BASE_MESSAGE = bytearray([255, 1, 0, 90, 255])
BEEP_MESSAGE = bytearray([255, 65, 1, 1, 255])
DEFAULT_POSITION = (100, 190)
BUTTON_HEIGHT = 105
OBJECT_HEIGHT = 8
TOP_POSITION = (5, 300)


class Arm(BaseModule):
    def __init__(self, s: socket.socket):
        super().__init__(s.dup())
        self.state = [0, 0, 0, 0]
        self.set_arm(*DEFAULT_POSITION, fast=True)
        self.rotate_hand_vertical()
        self.close_hand()

    @staticmethod
    def _calculate_angles(length: int, height: int) -> tuple[int, int]:
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

    def _send(self, message: bytearray, sleep_time=SLEEP_TIME) -> bool:
        return super()._send(message, sleep_time)

    def _make_message(self, servo: int, angle: int):
        if servo not in (1, 2, 3, 4):
            return BEEP_MESSAGE
        if angle > 170 or angle < 15:
            return BEEP_MESSAGE
        message = BASE_MESSAGE.copy()
        message[2] = servo
        message[3] = angle
        return message

    def _set_state(self, state: list[int]):
        order = (3, 4, 1, 2)
        if state[1] > self.state[1]:
            order = (3, 4, 2, 1)
        for servo in order:
            if self.state[servo - 1] == state[servo - 1]:
                continue
            if self._send(self._make_message(servo, state[servo - 1])):
                self.state[servo - 1] = state[servo - 1]

    def close_hand(self, ball: bool = False):
        state = self.state.copy()
        if ball:
            state[3] = 87
        else:
            state[3] = 77
        self._set_state(state)

    def open_hand(self):
        state = self.state.copy()
        state[3] = 50
        self._set_state(state)

    def rotate_hand_vertical(self):
        state = self.state.copy()
        state[2] = 170
        self._set_state(state)

    def rotate_hand_horizontal(self):
        state = self.state.copy()
        state[2] = 90
        self._set_state(state)

    def set_arm(self, length: int, height: int, fast: bool = False):
        state = self.state.copy()
        first, second = self._calculate_angles(length, height)
        print(f"{length, height}: Calculated angles are {first} and {second}")
        state[0], state[1] = (first + state[0]) // 2, (second + state[1]) // 2
        print(state)
        if not fast:
            self._set_state(state)
        state[0], state[1] = first, second
        print(state)
        self._set_state(state)

    def hit(self, length: int):
        self.rotate_hand_horizontal()
        self.close_hand()
        self.set_arm(*TOP_POSITION, fast=True)
        self.set_arm(length, 105, fast=True)

    def grab(self, length: int, ball: bool = False):
        if length > 250:
            print("WARNING. MAX prooved LENGTH IS 250, BUT YOUR'S IS %s", length)
        self.rotate_hand_horizontal()
        self.open_hand()
        self.set_arm(length, OBJECT_HEIGHT)
        self.close_hand(ball)
        self.default()
        self.rotate_hand_vertical()

    def default(self):
        self.set_arm(*DEFAULT_POSITION)
