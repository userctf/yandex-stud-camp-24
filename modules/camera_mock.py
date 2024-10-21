from os import listdir
from base_camera import BaseCamera, Prediction
import cv2
import numpy as np
from typing import Tuple, List
from os.path import isfile, join


class CameraMock():
    left_matrix = np.array([[850.07, 0., 929.22],
                            [0., 846.76, 575.28],
                            [0., 0., 1.]])
    left_dist_coefs = np.array([-0.2, 0.05, 0, 0, 0])

    def __init__(self, stream_url: str, neural_model: str, api_key: str):
        self.last_image_index = 0
        self.cropping_data = None

    @staticmethod
    def fix_eye(frame: np.ndarray, is_left: bool) -> np.ndarray:  # IMPORTANT: it crops a little bit
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        h, w = frame.shape[:2]
        camera_matrix = CameraMock.left_matrix
        dist_coefs = CameraMock.left_dist_coefs

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
    
    def get_photo(self) -> np.ndarray:
        imgs = []
        for file in listdir("imgs"):
            if isfile(join("imgs", file)) and (file.endswith(".png") or file.endswith(".jpg")):
                imgs.append(join("imgs", file))
        image = cv2.imread(imgs[self.last_image_index])
        self.last_image_index = (self.last_image_index + 1) % len(imgs)
        print("Getting image: ", image)
        return image


    def get_game_arena(self, frame: np.ndarray) -> (np.ndarray, int, int):
        min_area_box = self.__get_game_arena_min_box(frame)
        # using precalced data if possible
        if self.cropping_data is None:
            min_area_box = self.__get_game_arena_min_box(frame)
            box = np.int0(cv2.boxPoints(min_area_box))
            width, height = int(min_area_box[1][0]), int(min_area_box[1][1])
            
            src_pts = box.astype('float32')
            dst_pts = np.array([[0, height-1], [0, 0], [width-1, 0], [width-1, height-1]], dtype='float32')
            M = cv2.getPerspectiveTransform(src_pts, dst_pts)
            
            self.cropping_data = M, (width, height)
        
        M = self.cropping_data[0]
        width, height = self.cropping_data[1]
        min_area_box = self.__get_game_arena_min_box(frame)
        img_crop = cv2.warpPerspective(frame, M, (width, height))

        return img_crop, width, height
    
    @staticmethod
    def __get_game_arena_min_box(frame: np.array) -> ((int, int), (int, int), int): # center, size, angle
        img = frame[0:1400, 0:1600] # crop to remove extra data
        contours = CameraMock.get_all_contours(img)
        area_res = []

        for c in contours:
            # (center), (w/h), angle
            min_area_box = cv2.minAreaRect(c)
            area_res.append(min_area_box)
        
        if len(area_res) == 0:
            return (0, 0), (0, 0), 0
        return max(area_res, key=lambda box: box[1][0] * box[1][1])
    
    @staticmethod
    def detection_borders(frame: np.array) -> (bool, str):
        PADDING_Y = 20
        PADDING_X = 20
        box_x, box_y, box_w, box_h, _ = CameraMock.get_game_arena_size(frame)
        frame = frame[
                box_y + PADDING_Y:   box_y + box_h - 2 * PADDING_Y,
                box_x + PADDING_X:   box_x + box_w - 2 * PADDING_X
                ]  # crop to main rectangle

        contours = CameraMock.get_all_contours(frame)
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

    @staticmethod
    def __get_game_arena_min_box(frame: np.array) -> ((int, int), (int, int), int): # center, size, angle
        img = frame[0:1400, 0:1600] # crop to remove extra data
        contours = CameraMock.get_all_contours(img)
        area_res = []

        for c in contours:
            # (center), (w/h), angle
            min_area_box = cv2.minAreaRect(c)
            area_res.append(min_area_box)
        
        if len(area_res) == 0:
            return (0, 0), (0, 0), 0
        return max(area_res, key=lambda box: box[1][0] * box[1][1])
   
   
if __name__ == '__main__':
    camera = CameraMock("rtsp://Admin:rtf123@192.168.2.250:554/1", 'detecting_objects-ygnzn/1',
                       api_key="d6bnjs5HORwCF1APwuBX")
    while True:
        img = camera.get_photo()
        img = camera.fix_eye(img, True)
        img = camera.get_game_arena(img)[0]
        cv2.imshow('kek', img)
        cv2.waitKey(0)
