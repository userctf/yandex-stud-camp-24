import cv2
import time
import numpy as np
from typing import List, Tuple

from copy import deepcopy
from base_camera import Prediction

from top_camera import TopCamera
from utils.enums import GameObjectType, GameObjectPosition, ObjectType
from utils.position import Position
from utils.gameobject import GameObject

IS_LEFT = True

VIRTUAL_HEIGHT = 320
VIRTUAL_WIDTH = 400

LIGHT_THRESHOLD = 220
MIN_AREA_THRESHOLD = 100

GAME_OBJECTS_TEMPLATE = {
    GameObjectType.CUBE: [],
    GameObjectType.BALL: None,
    GameObjectType.GREEN_BASE: None,
    GameObjectType.RED_BASE: None,
    GameObjectType.OUR_ROBOT: None,
    GameObjectType.BAD_ROBOT: None,
    GameObjectType.BTN_PINK_BLUE: None,
    GameObjectType.BTN_GREEN_ORANGE: None,
}

class GameMap:
    def __init__(self, top_camera: TopCamera, color: str = "red"):
        self.top_camera = top_camera
        self.game_objects = deepcopy(GAME_OBJECTS_TEMPLATE)
        self.inner_boards = GameObjectPosition.UNKNOWN
        self.outer_boards = GameObjectPosition.UNKNOWN
        self.color = color
        self.limits = []  # первый элемент изменение по оси х, второй по оси у
        self._set_frame_limits()

    @staticmethod
    def _crop_to_robot(image: np.ndarray, robot: Prediction) -> Tuple[np.ndarray, Position]:
        top, bottom = robot.get_coords()
        cropped = image[top[1]:bottom[1], top[0]:bottom[0]]
        return cropped, Position(top[0], top[1])

    @staticmethod
    def _find_robot_color_and_position(cropped_frame: np.ndarray, color: str) -> Tuple[bool, Position]:
        height, width, _ = cropped_frame.shape

        center_region_size = 0.5
        center_x_start = int(width * (1 - center_region_size) / 2)
        center_y_start = int(height * (1 - center_region_size) / 2)
        center_x_end = int(width * (1 + center_region_size) / 2)
        center_y_end = int(height * (1 + center_region_size) / 2)

        center_position = Position(center_x_start, center_y_start)

        center = cropped_frame[center_y_start:center_y_end, center_x_start:center_x_end]

        gray_image = cv2.cvtColor(center, cv2.COLOR_BGR2GRAY)
        _, bright_mask = cv2.threshold(gray_image, LIGHT_THRESHOLD, 255, cv2.THRESH_BINARY)
        bright_pixels = cv2.bitwise_and(center, center, mask=bright_mask)

        non_black_pixels = bright_pixels[np.any(bright_pixels != [0, 0, 0], axis=-1)]

        mean_color = np.mean(non_black_pixels, axis=0)
        mean_blue, mean_green, mean_red = mean_color

        position = GameMap._find_angle(bright_mask) + center_position

        if mean_red > mean_green:
            print("Средний цвет ярких пикселей ближе к красному")
            return color == "red" and position.angle != -1, position
        else:
            print("Средний цвет ярких пикселей ближе к зелёному")
            return color == "green" and position.angle != -1, position

    @staticmethod
    def _find_angle(bright_mask: np.array) -> Position:
        contours, _ = cv2.findContours(bright_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        min_area = MIN_AREA_THRESHOLD  # Минимальная площадь облака, которое будем учитывать

        filtered_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_area]

        if not filtered_contours:
            print("Can't determine robot angle")
            print([cv2.contourArea(cnt) for cnt in contours])
            height, width = bright_mask.shape
            return Position(width // 2, height // 2, -1)

            # Выбираем самый крупный контур (основное облако)
        largest_contour = max(filtered_contours, key=cv2.contourArea)

        # Строим минимальный ограничивающий прямоугольник для самого крупного контура
        rect = cv2.minAreaRect(largest_contour)

        (cx, cy), (width, height), angle = rect

        # Если облако вытянуто, находим длинную сторону
        if width > height:
            main_angle = angle
        else:
            main_angle = angle + 90
        return Position(int(cx), int(cy), main_angle)

    def _set_frame_limits(self):
        # вызывается при инициализации. Нужен для перевода в координаты и обратно
        # frame = self.top_camera.get_photo()
        frame = cv2.imread("img.png")
        frame = self.top_camera.fix_eye(frame, IS_LEFT)

        _, w, h = self.top_camera.get_game_arena(frame)
        self.limits = [w / VIRTUAL_WIDTH, h / VIRTUAL_HEIGHT]

    def _frame_to_map_position(self, position: Position) -> Position:
        # Using limits from _set_frame_limits. Can't be made static
        position.x = int(position.x * self.limits[0] + 0.5)
        position.y = int(position.y * self.limits[1] + 0.5)
        return position

    def _get_robot_position(self, frame: np.ndarray, prediction: Prediction) -> Tuple[bool, Position]:
        cropped_frame, crop_position = GameMap._crop_to_robot(frame, prediction)
        is_our, robot_position = GameMap._find_robot_color_and_position(cropped_frame, self.color)
        return is_our, robot_position + crop_position

    def get_our_robot_position(self) -> GameObject:
        return self.game_objects[GameObjectType.OUR_ROBOT][0]

    def set_up_field(self):
        start_time = time.time()
        while time.time() - start_time < 2:
            frame = self.top_camera.get_photo()
            frame = self.top_camera.fix_eye(frame, IS_LEFT)
            frame, w, h = self.top_camera.get_game_arena(frame)

            predicts = sorted(self.top_camera.predict(frame), key=lambda p: p.object_type)
            print(predicts)

            for predict in predicts:
                if predict.object_type == ObjectType.CUBE:
                    pass



    def find_all_game_objects(self):
        # инициализация. Работает пока не заполним 2 куба, обоих роботов, обе базы, обе кнопки
        frame = self.top_camera.get_photo()
        # frame = cv2.imread("img.png")
        frame = self.top_camera.fix_eye(frame, IS_LEFT)

        frame, w, h = self.top_camera.get_game_arena(frame)

        predicts = self.top_camera.predict(frame)
        print(predicts)

        new_game_objects = deepcopy(GAME_OBJECTS_TEMPLATE)

        for predict in predicts:
            if predict.object_type is ObjectType.ROBOT:
                is_our, position = self._get_robot_position(frame, predict)
                robot_type = GameObjectType.OUR_ROBOT if is_our else GameObjectType.BAD_ROBOT
                new_game_objects[robot_type] = [GameObject(
                    position,
                    predict.get_size(),
                    robot_type,
                )]
                print(new_game_objects[GameObjectType.OUR_ROBOT])
                print(new_game_objects[GameObjectType.BAD_ROBOT])
            elif predict.object_type == ObjectType.CUBE:
                new_game_objects[GameObjectType.CUBE].append(
                    GameObject(np.int32(predict.center), predict.get_size(), GameObjectType.CUBE)
                )

        self.game_objects = new_game_objects


if __name__ == "__main__":
    camera = TopCamera("rtsp://Admin:rtf123@192.168.2.250:554/1", 'detecting_objects-ygnzn/1',
                       api_key="d6bnjs5HORwCF1APwuBX")
    game_map = GameMap(camera)
    game_map.find_all_game_objects()
    camera.stopped = True
    cv2.destroyAllWindows()
