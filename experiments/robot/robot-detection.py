from typing import Tuple

import cv2
import os
import sys

import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../modules')))
from modules.top_camera import TopCamera
from modules.base_camera import ObjectType, Prediction

camera = TopCamera("rtsp://Admin:rtf123@192.168.2.250:554/1", 'detecting_objects-ygnzn/1',
                   api_key="d6bnjs5HORwCF1APwuBX")

image = cv2.imread("left.jpg")
preds = camera.get_objects(image, ObjectType.ROBOT)
print(preds)

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


def find_robot_coordinates(image: np.array, robot: Prediction) -> Tuple[int, int, int]:
    cropped = crop_to_robot(image, robot)
    check_robot_color_and_angle(cropped, "green")



def crop_to_robot(image: np.array, robot: Prediction):
    top, bottom = robot.get_coords()
    cropped = image[top[1]:bottom[1], top[0]:bottom[0]]
    cv2.imshow('Original Image', cropped)
    cv2.waitKey(0)
    return cropped


def check_robot_color_and_angle(cropped: np.array, color: str) -> Tuple[bool, float]:
    height, width, _ = cropped.shape

    center_region_size = 0.5
    center_x_start = int(width * (1 - center_region_size) / 2)
    center_y_start = int(height * (1 - center_region_size) / 2)
    center_x_end = int(width * (1 + center_region_size) / 2)
    center_y_end = int(height * (1 + center_region_size) / 2)

    center = cropped[center_y_start:center_y_end, center_x_start:center_x_end]

    gray_image = cv2.cvtColor(center, cv2.COLOR_BGR2GRAY)
    _, bright_mask = cv2.threshold(gray_image, 200, 255, cv2.THRESH_BINARY)
    bright_pixels = cv2.bitwise_and(center, center, mask=bright_mask)

    non_black_pixels = bright_pixels[np.any(bright_pixels != [0, 0, 0], axis=-1)]

    mean_color = np.mean(non_black_pixels, axis=0)
    mean_blue, mean_green, mean_red = mean_color

    find_angle(bright_mask, bright_pixels)

    if mean_red > mean_green:
        print("Средний цвет ярких пикселей ближе к красному")
        return color == "red"
    else:
        print("Средний цвет ярких пикселей ближе к зелёному")
        return color == "green"


def find_angle(bright_mask: np.array, bright_pixels) -> float:
    contours, _ = cv2.findContours(bright_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    min_area = 150  # Минимальная площадь облака, которое будем учитывать

    filtered_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_area]

    if filtered_contours:
        # Выбираем самый крупный контур (основное облако)
        largest_contour = max(filtered_contours, key=cv2.contourArea)

        # Строим минимальный ограничивающий прямоугольник для самого крупного контура
        rect = cv2.minAreaRect(largest_contour)
        box = cv2.boxPoints(rect)
        box = np.int0(box)  # Приводим к целым числам

        # Рисуем ограничивающий прямоугольник на изображении (для визуализации)
        image_with_box = bright_pixels.copy()
        cv2.drawContours(image_with_box, [box], 0, (0, 255, 0), 2)

        # Центр прямоугольника и угол поворота
        (cx, cy), (width, height), angle = rect

        # Если облако вытянуто, находим длинную сторону и строим перпендикуляр
        if width > height:
            main_angle = angle
        else:
            main_angle = angle + 90

        # Перпендикулярный угол (90 градусов к основному углу)
        perp_angle = main_angle + 90

        # Длина линии перпендикуляра
        line_length = 100  # Длина перпендикуляра для наглядности

        # Вычисляем начальную и конечную точки линии перпендикуляра
        x1 = int(cx + line_length * np.cos(np.deg2rad(perp_angle)))
        y1 = int(cy + line_length * np.sin(np.deg2rad(perp_angle)))
        x2 = int(cx - line_length * np.cos(np.deg2rad(perp_angle)))
        y2 = int(cy - line_length * np.sin(np.deg2rad(perp_angle)))

        # Рисуем перпендикулярную линию через центр облака
        cv2.line(image_with_box, (x1, y1), (x2, y2), (255, 0, 0), 2)

        # Показываем результат
        cv2.imshow("Perpendicular Line", image_with_box)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        areas = [cv2.contourArea(cnt) for cnt in contours]
        print(areas)
    return .0


for robot in preds:
    find_robot_coordinates(image, robot)
