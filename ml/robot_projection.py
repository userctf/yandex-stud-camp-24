import time

import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt


LENGTH = 1200
HEIGHT = 2000


def convert_coord_to_mm(x: int, y: int) -> tuple[int, int]:
    # coords with respect to (0, 0) coord of arm
    x -= 600
    y = 2000 - y
    mm = 105
    pxl = 305
    return int(x * mm / pxl) + 75, int(y * mm / pxl) + 120


def get_projection_matrix(path: str) -> np.array:
    img = cv.imread('proj_photo_1.jpg')
    assert img is not None, "file could not be read, check with os.path.exists()"

    coord_on_photo_from_camera = [[154, 197], [27, 454], [488, 201], [607, 454]]
    # coord_on_projection_mm = [[-105, 290], [0, 0], [105, 290], [105, 10]] [321, 479]
    coord_on_projection_pxl = [[285, 1130], [285, 1970], [915, 1130], [915, 1970]]

    # Define source and destination points
    src_points = np.array(coord_on_photo_from_camera, dtype=np.float32)
    dst_points = np.array(coord_on_projection_pxl, dtype=np.float32)

    # Compute homography matrix
    transform_matrix, mask = cv.findHomography(src_points, dst_points, cv.RANSAC, 5.0)
    return transform_matrix


def find_projection_coord(x_src: int, y_src: int, proj_matrix: np.array) -> tuple[int, int]:
    x_dst = int((proj_matrix[0][0] * x_src + proj_matrix[0][1] * y_src + proj_matrix[0][2]) /
                (proj_matrix[2][0] * x_src + proj_matrix[2][1] * y_src + proj_matrix[2][2]))
    y_dst = int((proj_matrix[1][0] * x_src + proj_matrix[1][1] * y_src + proj_matrix[1][2]) /
                (proj_matrix[2][0] * x_src + proj_matrix[2][1] * y_src + proj_matrix[2][2]))
    return x_dst, y_dst


def show_projection_photo(path: str, proj_matrix: np.array):
    img = cv.imread(path)
    assert img is not None, "file could not be read, check with os.path.exists()"
    dst = cv.warpPerspective(img, proj_matrix, (LENGTH, HEIGHT))
    plt.imshow(dst)
    plt.show()

def example(x, y):
    m = get_projection_matrix('proj_photo.jpg')
    x, y = find_projection_coord(x, y, m)
    return convert_coord_to_mm(x, y)
