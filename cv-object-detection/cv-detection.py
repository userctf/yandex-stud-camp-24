import cv2
import time
from typing import Tuple

def HSV2BGR(frame):
    return cv2.cvtColor(frame, cv2.COLOR_HSV2BGR)

def apply_morph(frame, k_size=10, morph_type=cv2.MORPH_OPEN, iters=1):
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (k_size, k_size))
    return cv2.morphologyEx(frame, morph_type, kernel, iters)

def apply_binarization(frame, lower_b: Tuple[int, int, int], upper_b: Tuple[int, int, int]):
    return cv2.inRange(frame, lower_b, upper_b)

def apply_blur(frame, blur_val):
    return cv2.medianBlur(frame, 1 + blur_val * 2)

def get_edges(frame, lower, upper):
    return cv2.Canny(frame, lower, upper)

def get_contoures(edges):
    contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours


def borders_position(box):
    if box[0] > box[1]:
        return "Top/Bottom"
    else:
        return "Left/Right"

url = "rtsp://Admin:rtf123@192.168.2.251/251:554/1/1"

class CVDetection:
    def __init__(self, url: str):
        self.cap = cv2.VideoCapture(url)

    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            print("Error while reading frame")
        # return cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        return frame
    
    # def fix_fish_eye(frame, isLeft):
        

    def __del__(self):
        self.cap.release()
        cv2.destroyAllWindows()

model = CVDetection(url)
while True:
    original_frame = apply_blur(
        model.get_frame(),
        2
    )
    original_frame = original_frame[100:950, 300:1400]
    
    grey_frame = cv2.cvtColor(original_frame, cv2.COLOR_BGR2GRAY)
    # black_frame = apply_binarization(original_frame, (0, 0, 0), (255, 255, 40))
    _, binary_image = cv2.threshold(grey_frame, 90, 250, cv2.THRESH_BINARY)
    frame_morph = apply_morph(binary_image)
    
    edges = get_edges(frame_morph, 0, 250)
    contours = get_contoures(edges)
    res = []
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if w * h > 120_000:
            res.append((w, h))
            frame_morph = cv2.rectangle(frame_morph, (x, y), (x + w, y + h), (0, 255, 255), 2)
            
    print(borders_position(sorted(res, key=lambda i : i[0] * i[1], reverse=True)[0]))
    
    # frame = cv2.drawContours(original_frame, contours, -1, (0, 255, 0), 2)
    cv2.imshow("red_frame", frame_morph)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
