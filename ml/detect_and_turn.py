import requests
from inference import get_model
import cv2
import requests
import numpy as np
from time import sleep
from typing import Tuple, List

url = "http://192.168.2.106:8080/?action=stream"

IMAGE_CENTER: Tuple[float, float] = (640 / 2, 480 / 2)

class Prediction:
    def __init__(self, prediction):
        self.class_name: str = prediction.class_name
        self.confidence: float = prediction.confidence
        self.center: Tuple[float, float] = (prediction.x, prediction.y)
        self.points = prediction.points

    def get_delta(self, point: Tuple[float, float]) -> Tuple[float, float]:
        return (self.center[0] - point[0], self.center[1] -  point[1])

def predict(model, image) -> Prediction:
    results = model.infer(image, confidence=0.8)[0]
    print(results)
    return [Prediction(pred) for pred in results.predictions]


def read_stream(model):
    stream = requests.get(url, stream=True)
    read_bytes = bytes()
    for chunk in stream.iter_content(chunk_size=1024):
        read_bytes += chunk
        a = read_bytes.find(b'\xff\xd8')
        b = read_bytes.find(b'\xff\xd9')
        if a != -1 and b != -1:
            jpg = read_bytes[a:b+2]
            read_bytes = read_bytes[b+2:]
            print("Started to predict image")
            img = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
            results: List[Prediction] = predict(model, img)
            for item in results:
                print(item.__dict__)
            best_prediction = results[0]
            x_delta, y_delta = best_prediction.get_delta(IMAGE_CENTER)
            print(x_delta, y_delta)
            if abs(x_delta) > 5:
                pass
                """
                TODO:
                if x_delta < 0

                    turn_left(1 degree)
                else:
                    turn_right(1 degree)
                

                """


            stream.close()
            sleep(0.1)
            return


model = get_model(model_id="top-camera-detection-r4fqs/2", api_key="uGu8WU7fJgR8qflCGaqP")
for _ in range(5):
    read_stream(model)
    