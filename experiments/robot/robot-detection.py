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
im2 = image.copy()
preds = camera.get_objects(im2, ObjectType.ROBOT)
cv2.imshow("z", image)
print(preds)

COLORS = {
    "red": [
        (np.array([0, 50, 50]),
         np.array([10, 255, 255]),),
        (np.array([170, 50, 50]),
         np.array([180, 255, 255]),)
    ],
    "green": [
        (np.array([35, 40, 40]), np.array([85, 255, 255])),
    ]
}


def find_robot_coordinates(image: np.array, robot: Prediction) -> Tuple[int, int, int]:
    cropped = crop_to_robot(image, robot)
    check_robot_color(cropped, "green")

    pass


def crop_to_robot(image: np.array, robot: Prediction):
    top, bottom = robot.get_coords()
    cropped = image[top[1]:bottom[1], top[0]:bottom[0]]
    cv2.imshow('Original Image', cropped)
    cv2.waitKey(0)
    return cropped

def check_robot_color(cropped: np.array, color: str) -> bool:
    thresholds = COLORS[color]
    cropped = cropped.copy()
    res_mask = np.zeros(cropped.shape[0:2], np.uint8)
    for threshold in thresholds:
        mask = cv2.inRange(cropped, threshold[0], threshold[1])
        res_mask = cv2.bitwise_or(res_mask, mask)

    cv2.imshow('Original Image', res_mask)
    cv2.waitKey(0)
    return False

for robot in preds:
    find_robot_coordinates(image, robot)
