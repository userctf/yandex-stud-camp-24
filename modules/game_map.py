import cv2
import time
import numpy as np
from typing import List, Tuple

from copy import deepcopy

from numpy.lib.function_base import angle

from base_camera import Prediction

from top_camera import TopCamera

from utils.enums import GameObjectType, GameStartState, ObjectType
from utils.position import Position
from utils.gameobject import GameObject, Base
import a_star

IS_LEFT = True

VIRTUAL_HEIGHT = 320
VIRTUAL_WIDTH = 400

LIGHT_THRESHOLD = 220
MIN_AREA_THRESHOLD = 100
GAME_OBJECTS_TEMPLATE = {
    GameObjectType.CUBE: [],
    GameObjectType.BALL: [],
    GameObjectType.GREEN_BASE: [],
    GameObjectType.RED_BASE: [],
    GameObjectType.OUR_ROBOT: [],
    GameObjectType.BAD_ROBOT: [],
    GameObjectType.BTN_PINK_BLUE: [],
    GameObjectType.BTN_GREEN_ORANGE: [],
}

GAME_STATE_TEMPLATE = {
    GameObjectType.CUBE: GameStartState.UNKNOWN,
    GameObjectType.BALL: GameStartState.UNKNOWN,
    GameObjectType.GREEN_BASE: GameStartState.UNKNOWN,
    GameObjectType.RED_BASE: GameStartState.UNKNOWN,
    GameObjectType.OUR_ROBOT: GameStartState.OUTER_START_LIKE,
    GameObjectType.BAD_ROBOT: GameStartState.OUTER_START_LIKE,
    GameObjectType.BTN_PINK_BLUE: GameStartState.UNKNOWN,
    GameObjectType.BTN_GREEN_ORANGE: GameStartState.UNKNOWN,
}

class GameMap:
    def __init__(self, top_camera: TopCamera, is_left: bool = True, color: str = "red",):
        self.top_camera = top_camera
        self.game_objects = deepcopy(GAME_OBJECTS_TEMPLATE)
        self.inner_boards = GameStartState.UNKNOWN
        self.outer_boards = GameStartState.UNKNOWN
        self.state = deepcopy(GAME_STATE_TEMPLATE)
        self.is_left = is_left
        self.color = color
        self.limits = []  # первый элемент изменение по оси х, второй по оси у

        self._set_frame_limits()
        self.set_up_field()
        self.find_all_game_objects()
        
        self.a_star : a_star.AStarSearcher = GameMap._init_star(self.inner_boards, self.outer_boards)
        
    @staticmethod
    def _init_star(inner_boards, outer_boards) -> a_star.AStarSearcher:
        walls: List[Tuple[int, int]] = a_star.gen_default_walls()
        if inner_boards == GameStartState.HORIZONTAL:
            walls += a_star.gen_up_down_inner_walls()
        elif inner_boards == GameStartState.VERTICAL:
            walls += a_star.gen_left_right_inner_walls()
            
        if  outer_boards == GameStartState.HORIZONTAL:
            walls += a_star.gen_up_down_outer_walls()
        elif outer_boards == GameStartState.VERTICAL:
            walls += a_star.gen_left_right_outer_walls()
        return a_star.AStarSearcher(walls)

    def find_path_to(self, robot_position: Position, game_object_type: GameObjectType) -> List[Tuple[int, int]]:
        self.find_all_game_objects()
        
        start_point = robot_position # TODO: center or other point of robot???
        end_point = self.game_objects[game_object_type][0].position # TODO: find [0] or the closest one?

        path: List[Tuple[int, int]] = self.a_star.search_closest_path(start_point, end_point)
        print(path)
        x_out_path = []
        y_out_path = []
        for point in path:
            x_out_path.append(point[0][0])
            y_out_path.append(point[0][1])
        result = list(zip(x_out_path, y_out_path))
        print(result)
        return result
      
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
            print("Средний цвет ярких пикселей ближе к зелёному", position.angle)
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
        frame = self.top_camera.get_photo()
        # cv2.imshow("1ebala", frame)
        # cv2.waitKey(0)
        # frame = cv2.imread("img.png")
        frame = self.top_camera.fix_eye(frame, self.is_left)

        _, w, h = self.top_camera.get_game_arena(frame)
        print("Frame borders are:", w, h)
        self.limits = [w, h]

    def _frame_to_map_position(self, position: Position) -> Position:
        # Using limits from _set_frame_limits. Can't be made static
        position.x = int(position.x / self.limits[0] * VIRTUAL_WIDTH + 0.5)
        position.y = int(position.y / self.limits[1] * VIRTUAL_HEIGHT + 0.5)
        return position

    def _get_robot_position(self, frame: np.ndarray, prediction: Prediction) -> Tuple[bool, Position]:
        cropped_frame, crop_position = GameMap._crop_to_robot(frame, prediction)
        is_our, robot_position = GameMap._find_robot_color_and_position(cropped_frame, self.color)
        return is_our, robot_position + crop_position

    def _set_base_positions(self, base_prediction: Prediction):
        width, height = np.int32(base_prediction.get_size())
        print(width, height)
        x, y = np.int32(base_prediction.center)
        base_state = GameStartState.VERTICAL
        if width > height:
            base_state = GameStartState.HORIZONTAL
        print(base_state)
        if base_state == GameStartState.HORIZONTAL:
            self.state[GameObjectType.GREEN_BASE] = GameStartState.HORIZONTAL
            self.state[GameObjectType.RED_BASE] = GameStartState.HORIZONTAL
            self.state[GameObjectType.BTN_GREEN_ORANGE] = GameStartState.VERTICAL
            self.state[GameObjectType.BTN_PINK_BLUE] = GameStartState.VERTICAL
            red_x = x
            if y > 500:
                red_y = height // 3
            else:
                red_y = self.limits[1] - height // 3
        else:
            self.state[GameObjectType.GREEN_BASE] = GameStartState.VERTICAL
            self.state[GameObjectType.RED_BASE] = GameStartState.VERTICAL
            self.state[GameObjectType.BTN_GREEN_ORANGE] = GameStartState.HORIZONTAL
            self.state[GameObjectType.BTN_PINK_BLUE] = GameStartState.HORIZONTAL


            red_y = y
            if x > 600:
                red_x = width // 3
            else:
                red_x = self.limits[0] - width // 3

        width = width // 3 * 2
        height = height // 3 * 2
        green_position = self._frame_to_map_position(Position(x, y))
        red_position = self._frame_to_map_position(Position(red_x, red_y))
        conv_width, conv_height, _ = self._frame_to_map_position(Position(width, height))

        self.game_objects[GameObjectType.GREEN_BASE] = [
            Base(green_position, (conv_width, conv_height), GameObjectType.GREEN_BASE)]
        self.game_objects[GameObjectType.RED_BASE] = [
            Base(red_position, (conv_width, conv_height), GameObjectType.RED_BASE)]

    def get_our_robot(self) -> GameObject:
        return self.game_objects[GameObjectType.OUR_ROBOT][0]

    def set_up_field(self):
        start_time = time.time()
        while time.time() - start_time < 2:
            frame = self.top_camera.get_photo()
            # frame = cv2.imread("img.png")
            frame = self.top_camera.fix_eye(frame, self.is_left)
            frame, w, h = self.top_camera.get_game_arena(frame)

            # cv2.imshow("ebala", frame)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()

            predicts = sorted(self.top_camera.predict(frame), key=lambda p: p.object_type)
            print(predicts)

            for predict in predicts:
                if predict.object_type == ObjectType.CUBE:
                    pass
                elif predict.object_type == ObjectType.GREEN_BASE:
                    self._set_base_positions(predict)
                    print(self.game_objects[GameObjectType.GREEN_BASE])
                    print(self.game_objects[GameObjectType.RED_BASE])
            break


    def find_all_game_objects(self):
        # инициализация. Работает пока не заполним 2 куба, обоих роботов, обе базы, обе кнопки

        frame = self.top_camera.get_photo()
        # frame = cv2.imread("imgs/2024-10-21 18-13-51.mov_20241021_223737.300.png")

        frame = self.top_camera.fix_eye(frame, self.is_left)

        frame, w, h = self.top_camera.get_game_arena(frame)

        predicts = self.top_camera.predict(frame)
        print(predicts)

        new_game_objects = deepcopy(GAME_OBJECTS_TEMPLATE)

        for predict in predicts:
            if predict.object_type is ObjectType.ROBOT:
                is_our, position = self._get_robot_position(frame, predict)
                robot_type = GameObjectType.OUR_ROBOT if is_our else GameObjectType.BAD_ROBOT
                new_game_objects[robot_type] = [GameObject(
                    self._frame_to_map_position(position),
                    predict.get_size(),
                    robot_type,
                )]
                print(new_game_objects[GameObjectType.OUR_ROBOT])
                print(new_game_objects[GameObjectType.BAD_ROBOT])
            elif predict.object_type == ObjectType.CUBE:
                new_game_objects[GameObjectType.CUBE].append(
                    GameObject(self._frame_to_map_position(Position(*np.int32(predict.center))),
                               predict.get_size(),
                               GameObjectType.CUBE)
                )
        for key in self.game_objects.keys():
            if key == GameObjectType.GREEN_BASE:
                continue
            if key == GameObjectType.CUBE:
                self.game_objects[key] = new_game_objects[key].copy()
            elif key == GameObjectType.OUR_ROBOT:
                if len(new_game_objects[key]) == 0:
                    continue
                self.game_objects[key] = new_game_objects[key].copy()

        # self.game_objects = new_game_objects


if __name__ == "__main__":
    camera = TopCamera("rtsp://Admin:rtf123@192.168.2.250:554/1", 'detecting_objects-ygnzn/1',
                       api_key="d6bnjs5HORwCF1APwuBX")
    game_map = GameMap(camera, color="green")
    # game_map.set_up_field()
    game_map.find_all_game_objects()
    camera.stopped = True
    cv2.destroyAllWindows()
