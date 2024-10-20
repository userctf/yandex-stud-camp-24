import time
from typing import Tuple

import cv2
import os
import sys

import numpy as np
from jmespath.ast import projection

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../modules')))
from modules.top_camera import TopCamera
from modules.base_camera import ObjectType, Prediction

LIGHT_THRESHOLD = 225
MIN_AREA_THRESHOLD = 150

COLORS = {
    "red": [
        (np.array([0, 50, 50]),
         np.array([10, 255, 255]),),
        (np.array([170, 50, 50]),
         np.array([180, 255, 255]),)
    ],
    "green": [
        (np.array([35, 25, 25]), np.array([70, 255, 255])),
    ]
}


class Position:
    def __init__(self, x: int, y: int, angle: float = 0):
        self.x: int = x
        self.y: int = y
        self.angle: float = angle

    def __iter__(self):
        yield self.x
        yield self.y
        yield self.angle

    def __add__(self, other):
        return Position(self.x + other.x, self.y + other.y, self.angle)

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        return self

    def __repr__(self):
        return f"({self.x}, {self.y}), angle is {self.angle}"


def detect_robots(camera: TopCamera):
    image = camera.get_photo()
    image = camera.fix_eye(image, True)

    x, y, w, h = camera.get_game_arena_size(image)

    image = image[y:y + h, x:x + w]

    preds = camera.get_objects(image, ObjectType.ROBOT)

    cv2.imshow("cam", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    for robot in preds:
        start = time.time()
        find_robot_position(image, robot)
        print(time.time() - start, "find_robot_position time")


def find_robot_position(image: np.array, robot: Prediction):
    # image = camera.get_game_arena_size(image)

    cropped, position = crop_to_robot(image, robot)
    is_our, robot_position = find_robot_color_and_position(cropped, "green")
    print(f"This is {'our' if is_our else 'bad'} Robot position is", robot_position + position)


def crop_to_robot(image: np.array, robot: Prediction) -> Tuple[np.array, Position]:
    top, bottom = robot.get_coords()
    cropped = image[top[1]:bottom[1], top[0]:bottom[0]]

    # cv2.imshow('Original Image', cropped)
    # cv2.waitKey(0)
    return cropped, Position(top[0], top[1])


def find_robot_color_and_position(cropped: np.array, color: str) -> Tuple[bool, Position]:
    height, width, _ = cropped.shape

    center_region_size = 0.5
    center_x_start = int(width * (1 - center_region_size) / 2)
    center_y_start = int(height * (1 - center_region_size) / 2)
    center_x_end = int(width * (1 + center_region_size) / 2)
    center_y_end = int(height * (1 + center_region_size) / 2)

    center_position = Position(center_x_start, center_y_start)

    center = cropped[center_y_start:center_y_end, center_x_start:center_x_end]

    gray_image = cv2.cvtColor(center, cv2.COLOR_BGR2GRAY)
    _, bright_mask = cv2.threshold(gray_image, LIGHT_THRESHOLD, 255, cv2.THRESH_BINARY)
    bright_pixels = cv2.bitwise_and(center, center, mask=bright_mask)

    non_black_pixels = bright_pixels[np.any(bright_pixels != [0, 0, 0], axis=-1)]

    mean_color = np.mean(non_black_pixels, axis=0)
    print(mean_color)
    mean_blue, mean_green, mean_red = mean_color

    position = find_angle(bright_mask) + center_position

    if mean_red > mean_green:
        print("Средний цвет ярких пикселей ближе к красному")
        return color == "red" and position.angle != -1, position
    else:
        print("Средний цвет ярких пикселей ближе к зелёному")
        return color == "green" and position.angle, position


def find_angle(bright_mask: np.array, ) -> Position:
    contours, _ = cv2.findContours(bright_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    min_area = MIN_AREA_THRESHOLD  # Минимальная площадь облака, которое будем учитывать

    filtered_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_area]

    if not filtered_contours:
        print("Can't determine robot angle")
        areas = [cv2.contourArea(cnt) for cnt in contours]
        print(areas)
        return Position(0, 0, -1)

        # Выбираем самый крупный контур (основное облако)
    largest_contour = max(filtered_contours, key=cv2.contourArea)

    # Строим минимальный ограничивающий прямоугольник для самого крупного контура
    rect = cv2.minAreaRect(largest_contour)

    (cx, cy), (width, height), angle = rect

    # Если облако вытянуто, находим длинную сторону
    if width > height:
        main_angle = angle
    else:
        main_angle = angle + 90
    print("Calculate angle is ", main_angle, "pos is", int(cx), int(cy))
    return Position(int(cx), int(cy), main_angle)


if __name__ == "__main__":
    camera = TopCamera("rtsp://Admin:rtf123@192.168.2.250:554/1", 'detecting_objects-ygnzn/1',
                       api_key="d6bnjs5HORwCF1APwuBX")
    detect_robots(camera)
    cv2.destroyAllWindows()
