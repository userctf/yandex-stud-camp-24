from module import BaseModule

from inference import get_model
import numpy
import socket
from typing import Tuple, List


class ISensors(Sensors):    
    def __init__(self, s: socket.socket, onboard_stream_url: str, upper_stream_url: str, api_key: str):
        super().__init__(s.dup(), onboard_stream_url, upper_stream_url)    
        self.model = get_model(model_id="top-camera-detection-r4fqs/2", api_key=api_key)

    def __find_object(self, image: numpy.ndarray):
        found_objects = self.__predict(image)
        for object in found_objects:
            print(object.__dict__)
                
    def __predict(self, image: numpy.ndarray) -> List[Prediction]:
        results = self.model.infer(image)[0]
        return [Prediction(pred) for pred in results.predictions]


class Prediction:
    def __init__(self, prediction):
        self.class_name: str = prediction.class_name
        self.confidence: float = prediction.confidence
        self.position: Tuple[float, float] = (prediction.x, prediction.y)