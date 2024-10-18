from inference import get_model
from enum import Enum
import cv2
import numpy
from typing import Tuple, List
import requests


class ObjectType(Enum):
    CUBE = 0
    BALL = 1    # it is detecting only by on board cam
    BASKET = 2  # it is detecting only by on board cam
    BUTTONS = 3 # it is detecting only by on board cam
    ROBOT = 4
    GREEN_BASE = 5
    BTN_G_O = 6
    BTN_P_B = 7
    

class Prediction:
    def __init__(self, prediction):
        self.name: str = prediction.class_name
        self.object_type: ObjectType = Prediction.__get_type(prediction.class_name)
        self.confidence: float = prediction.confidence
        self.center: Tuple[float, float] = (prediction.x, prediction.y)
        self.size: Tuple[float, float] = (prediction.width, prediction.height)
        
    def get_coords(self) -> Tuple:
        left_top = (
            int(self.center[0] - 0.5 * self.size[0]), 
            int(self.center[1] - 0.5 * self.size[1])
        )
        right_bottom = (
            int(self.center[0] + 0.5 * self.size[0]), 
            int(self.center[1] + 0.5 * self.size[1])
        )
        
        return left_top, right_bottom
    
    def get_color(self) -> Tuple:
        if self.object_type == ObjectType.BALL:
            return (0, 115, 255) # orange
        elif self.object_type == ObjectType.CUBE:
            return (0, 10, 255) # red
        elif self.object_type == ObjectType.BASKET:
            return (28, 28, 28) # black
        elif self.object_type == ObjectType.BUTTONS:
            return (94, 81, 81) # grey
        elif self.object_type == ObjectType.ROBOT:
            return (203, 89, 23) # blue
        
    @staticmethod
    def __get_type(name: str) -> ObjectType:
        if name == "red cube":
            return ObjectType.CUBE
        elif name == "orange ball":
            return ObjectType.BALL
        elif name == "grey basket":
            return ObjectType.BASKET
        elif name == "junction box":
            return ObjectType.BUTTONS
        elif name == "robot":
            return ObjectType.ROBOT
        elif name == "green base":
            return ObjectType.GREEN_BASE
        elif name == "button green":
            return ObjectType.BTN_G_O
        elif name == "button blue":
            return ObjectType.BTN_P_B
        else:
            print("[ERROR] Can not find name ", name)


class BaseCamera:
    CONFIDENCE = 0.5
    
    def __init__(self, stream_url: str, neural_model: str, api_key: str):
        print("[INFO] start initiating camera")
        self.stream_url = stream_url
        self.model = get_model(model_id=neural_model, api_key=api_key)
        print("[INFO] neural model loaded")
        self.cap = cv2.VideoCapture(stream_url)
        print("[INFO] video capturing started")
        
    # get photo from stream
    def get_photo(self) -> numpy.ndarray:
        ret, frame = self.cap.read()
        if not ret:
            print("[ERROR] while reading frame")
        return frame
        
    def _write_on_img(self, frame: numpy.ndarray, predictions: List[Prediction]):
        for pred in predictions:
            left_up, right_down = pred.get_coords()
            color = pred.get_color()
            
            white_color = (255, 255, 255)  # White color in BGR
            cv2.putText(frame, pred.name + ":" + str(round(pred.confidence, 3)), (left_up[0], left_up[1] - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, white_color, 2)
            cv2.rectangle(frame, left_up, right_down, color, 2)
    
    # working with neural model
    def get_objects(self, frame: numpy.ndarray, object: ObjectType) -> List[Prediction]:
        found_objects = self._predict(frame)
        
        correct_objects = filter(lambda predict: predict.object_type == object, found_objects)
        return sorted(correct_objects, key=lambda pred: pred.confidence, reverse=True)
                
    def _predict(self, frame: numpy.ndarray) -> List[Prediction]:
        results = self.model.infer(frame, confidence=self.CONFIDENCE)[0]
        return [Prediction(pred) for pred in results.predictions]
    
    def __del__(self):
        self.cap.release()
    
    # test
    def test(self):
        while True:
            img = self.get_photo()
            p = self._predict(img)
            self._write_on_img(img, p)
            
            cv2.imshow('Frame with Box', img)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cv2.destroyAllWindows()


if __name__ == "__main__":
    BC = BaseCamera("http://192.168.2.106:8080/?action=stream", "robot_camera_detector/1", "uGu8WU7fJgR8qflCGaqP")
    BC.test()


