import cv2
import time
from typing import Tuple

url = "http://192.168.2.106:8080/?action=stream"

class CVDetection:
    def __init__(self, url: str):
        self.cap = cv2.VideoCapture(url)

    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            print("Error while reading frame")
        # return cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        return frame
    
    def HSV2BGR(self, frame):
        return cv2.cvtColor(frame, cv2.COLOR_HSV2BGR)
    
    def apply_morph(self, frame, k_size=10, morph_type=cv2.MORPH_OPEN, iters=1):
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (k_size, k_size))
        return cv2.morphologyEx(frame, morph_type, kernel, iters)
    
    def apply_binarization(self, frame, lower_b: Tuple[int, int, int], upper_b: Tuple[int, int, int]):
        return cv2.inRange(frame, lower_b, upper_b)
    
    def apply_blur(self, frame, blur_val):
        return cv2.medianBlur(frame, 1 + blur_val * 2)
    
    def get_edges(self, frame, lower, upper):
        return cv2.Canny(frame, lower, upper)
    
    
    def get_contoures(self, edges):
        contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return contours

    def __del__(self):
        self.cap.release()
        cv2.destroyAllWindows()

model = CVDetection(url)
while True:
    original_frame = model.apply_blur(
                model.get_frame(), 5
            )
    edges = model.get_edges(cv2.cvtColor(original_frame, cv2.COLOR_BGR2GRAY), 100, 200)
    contours = model.get_contoures(edges)
    frame = cv2.drawContours(original_frame, contours, -1, (0, 255, 0), 2)
        
    cv2.imshow("red_frame", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
