from module import BaseModule
from sensors import Sensors

from inference import get_model
import numpy
import cv2
import socket
from enum import Enum
from typing import Tuple, List


class Color(Enum):
    CUBE = 0
    BALL = 1
    BASKET = 2
    BUTTONS = 3

class Prediction:
    def __init__(self, prediction):
        self.class_name: str = prediction.class_name
        self.confidence: float = prediction.confidence
        self.center: Tuple[float, float] = (prediction.x, prediction.y)
        self.points = prediction.points
        
    def get_coords(self) -> Tuple:
        left_top = self.points[0]
        # left_bottom = 
        right_bottom = self.points[2]
        # right_top = 
        
        return (left_top, right_bottom)
        

class ISensors(Sensors):
    CONFIDENCE = 0.4
    
    def __init__(self, s: socket.socket, onboard_stream_url: str, upper_stream_url: str, api_key: str):
        super().__init__(s.dup(), onboard_stream_url, upper_stream_url)    
        self.model = get_model(model_id="top-camera-detection-r4fqs/2", api_key=api_key)
        
    def test(self):
        while True:
            img = self.get_photo(is_onboard_cap=True)
            p = self.__predict(img)
            # frame = self._write_on_img(img, p)
            
            cv2.imshow('Frame with Box', img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cv2.destroyAllWindows()
            
        
    def _write_on_img(self, frame: numpy.ndarray, predictions: List[Prediction]) -> numpy.ndarray:
        for pred in predictions:
            left_up, right_down = pred.get_coords()
            print("debug: ", left_up, right_down)
            color = (0, 255, 255)
            # frame = cv2.rectangle(frame, left_up, right_down, color, 2)

        return frame

    def __find_object(self, image: numpy.ndarray):
        found_objects = self.__predict(image)
        for object in found_objects:
            print(object.__dict__)
                
    def __predict(self, image: numpy.ndarray) -> List[Prediction]:
        results = self.model.infer(image, confidence=self.CONFIDENCE)[0]
        return [Prediction(pred) for pred in results.predictions]



host = "192.168.2.106"

port = 2055

# Создаем сокет
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print(f"Соединение с {host}:{port}")

# Устанавливаем соединение
s.connect((host, port))      
s = ISensors(s, "http://192.168.2.106:8080/?action=stream", None, "uGu8WU7fJgR8qflCGaqP")
s.test()

s.close()