import requests
from inference import get_model
import cv2
import requests
import numpy as np
from typing import Tuple

url = "http://192.168.2.106:8080/?action=stream"

class Prediction:
    def __init__(self, prediction):
        self.class_name: str = prediction.class_name
        self.confidence: float = prediction.confidence
        self.position: Tuple[float, float] = (prediction.x, prediction.y)

def predict(model, image) -> Prediction:
    results = model.infer(image)[0]
    return [Prediction(pred) for pred in results.predictions]

def read_stream(model):
    stream = requests.get(url, stream=True)
    read_bytes = bytes()
    for chunk in stream.iter_content(chunk_size=1024):
        # print('read yet another chunk')
        read_bytes += chunk
        a = read_bytes.find(b'\xff\xd8')
        b = read_bytes.find(b'\xff\xd9')
        if a != -1 and b != -1:
            jpg = read_bytes[a:b+2]
            read_bytes = read_bytes[b+2:]
            print("Started to predict image")
            img = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
            results = predict(model, img)
            for item in results:
                print(item.__dict__)

model = get_model(model_id="top-camera-detection-r4fqs/2", api_key="uGu8WU7fJgR8qflCGaqP")
read_stream(model)