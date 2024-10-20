from base_camera import BaseCamera, Prediction
import cv2
import numpy as np
from typing import Tuple, List


class TopCamera(BaseCamera):
    left_matrix = np.array([[850.07, 0., 929.22],
                            [0., 846.76, 575.28],
                            [0., 0., 1.]])
    right_matrix = np.array([[1182.719, 0., 927.03],
                             [0., 1186.236, 609.52],
                             [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
    left_dist_coefs = np.array([-0.2, 0.05, 0, 0, 0])
    right_dist_coefs = np.array([-0.5, 0.3, 0, 0, 0])

    def __init__(self, stream_url: str, neural_model: str, api_key: str):
        super().__init__(stream_url, neural_model, api_key)

    @staticmethod
    def fix_eye(frame: np.ndarray, is_left: bool) -> np.ndarray:  # IMPORTANT: it crops a little bit
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        h, w = frame.shape[:2]
        camera_matrix = TopCamera.left_matrix if is_left else TopCamera.right_matrix
        dist_coefs = TopCamera.left_dist_coefs if is_left else TopCamera.right_dist_coefs

        new_camera_mtx, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, dist_coefs, (w, h), 1, (w, h))

        dst = cv2.undistort(frame, camera_matrix, dist_coefs, None, new_camera_mtx)

        dst = cv2.cvtColor(dst, cv2.COLOR_BGR2RGB)

        # crop and save the image
        x, y, w, h = roi
        return dst[y - 20:y + h, x:x + w]

    @staticmethod
    def get_all_contours(frame: np.array) -> List:
        grey_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blured_frame = cv2.medianBlur(grey_frame, 5)

        _, binary_image = cv2.threshold(blured_frame, 90, 250, cv2.THRESH_BINARY)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 10))
        frame_morph = cv2.morphologyEx(binary_image, cv2.MORPH_OPEN, kernel, 1)

        edges = cv2.Canny(frame_morph, 0, 250)
        contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return contours

    @staticmethod
    def get_game_arena_size(frame: np.array) -> (int, int, int, int):  # x y w h from top left angle
        x_offset = 100
        img = frame[0:1400, x_offset:1600]  # crop to remove extra data
        contours = TopCamera.get_all_contours(img)
        area_res = []

        for c in contours:
            # x y w h
            area_res.append(cv2.boundingRect(c))

        ans = sorted(area_res, key=lambda box: box[2] * box[3], reverse=True)
        if len(ans) == 0:
            return (0, 0, 0, 0)
        return (ans[0][0] + x_offset, ans[0][1], ans[0][2], ans[0][3])
        # example of use: frame[box_y:box_y+box_h, box_x:box_x+box_w]

    @staticmethod
    def detection_borders(frame: np.array) -> (bool, str):
        PADDING_Y = 20
        PADDING_X = 20
        box_x, box_y, box_w, box_h, _ = TopCamera.get_game_arena_size(frame)
        frame = frame[
                box_y + PADDING_Y:   box_y + box_h - 2 * PADDING_Y,
                box_x + PADDING_X:   box_x + box_w - 2 * PADDING_X
                ]  # crop to main rectangle

        contours = TopCamera.get_all_contours(frame)
        res = []
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            if w * h > 120_000:  # BIG_NUMBER
                res.append((w, h))

        res.sort(key=lambda i: i[0] * i[1], reverse=True)  # find the biggest by area
        if res[0][0] > res[0][1]:
            return (True, "Top/Bottom")
        else:
            return (False, "Left/Right")


if __name__ == '__main__':
    camera = TopCamera("rtsp://Admin:rtf123@192.168.2.250:554/1", 'detecting_objects-ygnzn/1',
                       api_key="d6bnjs5HORwCF1APwuBX")
    img = camera.get_photo()
    img = camera.fix_eye(img, True)
    print(camera.detection_borders(img))
