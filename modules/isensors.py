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
        # print("debug:", prediction)
        self.class_name: str = prediction.class_name
        self.object_type: ObjectType = Prediction.__get_type(prediction.class_name)
        self.confidence: float = prediction.confidence
        self.center: Tuple[float, float] = (prediction.x, prediction.y)
        self.size: Tuple[float, float] = (prediction.width, prediction.height)
        
    def get_coords(self) -> Tuple:
        left_top = (
            int(self.center[0] - 0.5 * self.size[0]), 
            int(self.center[1] - 0.5 * self.size[1])
        )
        # left_bottom = 
        right_bottom = (
            int(self.center[0] + 0.5 * self.size[0]), 
            int(self.center[1] + 0.5 * self.size[1])
        )
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
        
        
    def __get_type(name: str) -> ObjectType:
        if name == "red cube":
            return ObjectType.CUBE
        elif name == "orange ball":
            return ObjectType.BALL
        elif name == "grey basket":
            return ObjectType.BASKET
        elif name == "junction box":
            return ObjectType.BUTTONS
        else:
            print("[ERROR] Can not find name ", name)

class ISensors(Sensors):
    CONFIDENCE = 0.5
        
    def __init__(self, s: socket.socket, onboard_stream_url: str, upper_stream_url: str, api_key: str):
        super().__init__(s.dup(), onboard_stream_url, upper_stream_url)    
        self.model = get_model(model_id="robot_camera_detector/1", api_key=api_key)
        
    def test(self):
        while True:
            img = self.get_photo(is_onboard_cap=True)
            p = self.__predict(img)
            frame = self._write_on_img(img, p)
            
            cv2.imshow('Frame with Box', img)
            print("len to box:", self.get_len_to(ObjectType.CUBE))
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cv2.destroyAllWindows()
        
    def get_len_to(self, object: ObjectType) -> (int, int):
        frame = self.get_photo(is_onboard_cap=True)
        items = self.__get_objects(frame, object)
        if len(items) == 0:
            return -1
        most_relevant = items[0]
        coords = most_relevant.get_coords()
        obj_x = (coords[0][0] + coords[1][0]) // 2
        obj_y = coords[1][1]
        return self.__get_mm_by_coords(obj_x, obj_y)
        
    def __get_mm_by_coords(self, x: int, y: int) -> (int, int):
        m = self.__get_projection_matrix()
        proj_x, proj_y = self.__find_projection_coord(x, y, m)
        return self.__convert_coord_to_mm(proj_x, proj_y)
        
    def __convert_coord_to_mm(self, x: int, y: int) -> tuple[int, int]:
        # coords with respect to (0, 0) coord of arm
        x -= 600
        y = 2000 - y
        mm = 105
        pxl = 305
        return int(x * mm / pxl) + 75, int(y * mm / pxl) + 120
    
    def __get_projection_matrix(self) -> numpy.array:
        # precalced (see algo in git ml/robot_projection.py)
        transform_matrix = numpy.array([[ 4.06696294e+00,  3.85634343e+00, -7.50161575e+02],
                                    [-3.55573093e-01,  1.98806608e+01, -1.34064097e+03],
                                    [-1.80493956e-04,  6.39010156e-03,  1.00000000e+00]])
        return transform_matrix
    
    def __find_projection_coord(self, x_src: int, y_src: int, proj_matrix: numpy.array) -> tuple[int, int]:
        x_dst = int((proj_matrix[0][0] * x_src + proj_matrix[0][1] * y_src + proj_matrix[0][2]) /
                    (proj_matrix[2][0] * x_src + proj_matrix[2][1] * y_src + proj_matrix[2][2]))
        y_dst = int((proj_matrix[1][0] * x_src + proj_matrix[1][1] * y_src + proj_matrix[1][2]) /
                    (proj_matrix[2][0] * x_src + proj_matrix[2][1] * y_src + proj_matrix[2][2]))
        return x_dst, y_dst
    
    def __show_projection_photo(self, path: str, proj_matrix: numpy.array):
        img = cv2.imread(path)
        assert img is not None, "file could not be read, check with os.path.exists()"
        dst = cv2.warpPerspective(img, proj_matrix, (LENGTH, HEIGHT))
        plt.imshow(dst)
        plt.show()
        
    def _write_on_img(self, frame: numpy.ndarray, predictions: List[Prediction]) -> numpy.ndarray:
        for pred in predictions:
            left_up, right_down = pred.get_coords()
            color = pred.get_color()
            
            white_color = (255, 255, 255)  # White color in BGR
            frame = cv2.putText(frame, str(round(pred.confidence, 3)), (left_up[0], left_up[1] - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, white_color, 2)
            frame = cv2.rectangle(frame, left_up, right_down, color, 2)

        return frame

    def __get_objects(self, image: numpy.ndarray, object: ObjectType) -> List[Prediction]:
        found_objects = self.__predict(image)
        res = []
        for found_object in found_objects:
            if found_object.object_type == object:
                res.append(found_object)
                
        return sorted(res, key=lambda pred: pred.confidence, reverse=True)
                
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
S = ISensors(s, "http://192.168.2.106:8080/?action=stream", None, "uGu8WU7fJgR8qflCGaqP")
S.test()
print("len to box:", self.get_len_to(ObjectType.CUBE))

s.close()