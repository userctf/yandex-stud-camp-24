from base_camera import BaseCamera, Prediction
import cv2
import numpy as np
from typing import Tuple, List
import cProfile

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

    def fix_eye_by_path(self, path_to_img: str, path_to_res: str, is_left: bool):
        img = cv2.imread(path_to_img)

        dst = self.fix_eye(img, is_left)
        # print('Undistorted image written to: %s' % path_to_res)
        cv2.imwrite(path_to_res, dst)

    def fix_eye(self, img: np.array, is_left: bool) -> np.array:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        h, w = img.shape[:2]
        camera_matrix = self.left_matrix if is_left else self.right_matrix
        dist_coefs = self.left_dist_coefs if is_left else self.right_dist_coefs

        new_camera_mtx, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, dist_coefs, (w, h), 1, (w, h))

        dst = cv2.undistort(img, camera_matrix, dist_coefs, None, new_camera_mtx)

        dst = cv2.cvtColor(dst, cv2.COLOR_BGR2RGB)

        # crop and save the image
        x, y, w, h = roi
        dst = dst[y - 20:y + h, x:x + w]

        # print('Undistorted image written to: %s' % path_to_res)
        return dst

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
        
    def get_game_arena_size(self, frame: np.array) -> (int, int, int, int):
        img = img[0:1400, 100:1600]
        contours = TopCamera.get_all_contours(img)
        area_res = []
        
        for c in contours:
            # x y w h
            area_res.append(cv2.boundingRect(c))
        
        ans = sorted(area_res, key=lambda box: box[2] * box[3], reverse=True)[0]
        ans[2] += 100
        return ans

    
        # while True:
        #     img = self.get_photo()
        #     img = self.fix_eye(img, True)[0:1400, 100:1600]
            
        #     contours = TopCamera.get_all_contours(img)
            
        #     for c in contours:
        #         x, y, w, h = cv2.boundingRect(c)
        #         if w * h > 110_000:
        #             img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 255), 2)
        #     cv2.imshow('Frame with Box', img)
            
        #     if cv2.waitKey(1) & 0xFF == ord('q'):
        #         break
        
        # cv2.destroyAllWindows()

    
    
    @staticmethod
    def detection_borders(frame: np.array) -> str:
        contours = TopCamera.get_all_contours(frame, (100, 900, 400, 1300))
        res = []
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            if w * h > 120_000: # BIG_NUMBER
                res.append((w, h))
                
        res.sort(key=lambda i: i[0] * i[1], reverse=True) # find the biggest by area
        if res[0][0] > res[0][1]:
            return "Top/Bottom"
        else:
            return "Left/Right"
        
    # test
    def test(self):
        while True:
            # cProfile.run('self.operate_frame()')
            self.operate_frame()
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cv2.destroyAllWindows()
    
    def operate_frame(self):
        img = self.get_photo()
        img = self.fix_eye(img, True)
        
        crop = self.get_game_arena_size(img)
        img = img[crop[0]:crop[1], crop[2]:crop[3]]
        
        p = self._predict(img)
        self._write_on_img(img, p)
        
        cv2.imshow('Frame with Box', img)


if __name__ == '__main__':
    camera = TopCamera("rtsp://Admin:rtf123@192.168.2.250:554/1", 'detecting_objects-ygnzn/1', api_key="d6bnjs5HORwCF1APwuBX")
    # img = cv2.imread("C:\\Users\\alexk\OneDrive\Documents\Studcamp-Yandex-2024\\right_output\output_frame_0016_fixed.png")
    # print(camera.detection_borders(img))
    # img = camera.get_photo()
    # print(camera.detection_borders(img))
    # camera.get_game_arena_size(None)
    camera.test()
    # cProfile.run('camera.operate_frame()')
