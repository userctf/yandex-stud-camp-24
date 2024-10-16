from module import BaseModule
from sensors import Sensors

from time import sleep
from inference import get_model
import numpy
import cv2
import socket
from enum import Enum
from typing import Tuple, List


class ObjectType(Enum):
    CUBE = 0
    BALL = 1
    BASKET = 2
    BUTTONS = 3

class Prediction:
    def __init__(self, prediction):
        self.class_name: str = prediction.class_name
        self.object_type: ObjectType = Prediction.get_type(prediction.class_name)
        self.confidence: float = prediction.confidence
        self.center: Tuple[float, float] = (prediction.x, prediction.y)
        self.points = [(int(pred.x), int(pred.y)) for pred in prediction.points]
        
    def get_coords(self) -> Tuple:
        left_top = self.points[0]
        # left_bottom = 
        right_bottom = self.points[2]
        # right_top = 
        
        return (left_top, right_bottom)
    
    def get_color(self) -> Tuple:
        if self.object_type == ObjectType.BALL:
            return (0, 115, 255) # orange
        elif self.object_type == ObjectType.CUBE:
            return (0, 10, 255) # red
        elif self.object_type == ObjectType.BASKET:
            return (28, 28, 28) # black
        elif self.object_type == ObjectType.BUTTONS:
            return (94, 81, 81) # grey
        
        
    def get_type(name: str) -> ObjectType:
        print("debug: ", name)
        if name == "red cube":
            return ObjectType.CUBE
        elif name == "orange ball":
            return ObjectType.BALL
        elif name == "grey basket":
            return ObjectType.BASKET
        elif name == "junction box":
            return ObjectType.BUTTONS

class ISensors(Sensors):
    CONFIDENCE = 0.5
    
    def __init__(self, s: socket.socket, onboard_stream_url: str, upper_stream_url: str, api_key: str):
        super().__init__(s.dup(), onboard_stream_url, upper_stream_url)    
        self.model = get_model(model_id="top-camera-detection-r4fqs/2", api_key=api_key)
        
    def test(self):
        while True:
            img = self.get_photo(is_onboard_cap=True)
            p = self.__predict(img)
            frame = self._write_on_img(img, p)
            
            cv2.imshow('Frame with Box', img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            sleep(0.1)
        
        cv2.destroyAllWindows()
            
        
    def _write_on_img(self, frame: numpy.ndarray, predictions: List[Prediction]) -> numpy.ndarray:
        for pred in predictions:
            left_up, right_down = pred.get_coords()
            print("debug: ", left_up, right_down)
            color = pred.get_color()
            
            white_color = (255, 255, 255)  # White color in BGR
            frame = cv2.putText(frame, str(round(pred.confidence, 3)), (left_up[0], left_up[1] - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, white_color, 2)
            frame = cv2.rectangle(frame, left_up, right_down, color, 2)

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