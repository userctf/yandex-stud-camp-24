from typing import List, Tuple
import cv2
import heapq
import math
from math import ceil
import matplotlib.pyplot as plt
import numpy as np

from base_camera import ObjectType


class GameObject:
    objtype: ObjectType
    x: int
    y: int

    def __init__(self, x: int, y: int, objtype=ObjectType.UNKNOWN):
        self.objtype = objtype
        self.x = x
        self.y = y


class _PriorityQueue:
    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def get(self):
        return heapq.heappop(self.elements)[1]


class Node:
    def __init__(self, x, y, cost, path):
        self.x = x
        self.y = y
        self.cost = cost
        self.path = path

    def __lt__(self, other) -> bool:
        return self.cost < other.cost

    def __str__(self):
        return (
            str(self.x)
            + "+"
            + str(self.y)
            + ","
            + str(self.cost)
            + ","
            + str(self.path)
        )


def _transform_path(x_path, y_path):
    new_path = np.array(list(zip(x_path, y_path))).astype(np.float32)
    path_len = cv2.arcLength(new_path, False)
    epsilon = 0.05 * path_len  # TODO: подобрать epsilon!!!!
    approx = cv2.approxPolyDP(new_path, epsilon, False)
    return approx


class AStarSearcher:
    def __init__(self, obstacles: List[Tuple[int, int]]):
        self.HEIGHT = 401
        self.WIDTH = 321
        self.GRID_SIZE = 4.0
        self.ROBOT_RADIUS = 10.0

        self._show_animation = True
        x_obstacle = [x for x, _ in obstacles]
        y_obstacle = [y for _, y in obstacles]
        self._path = self.__get_path()

        self._x_width = round((self.WIDTH) / self.GRID_SIZE)
        self._y_width = round((self.HEIGHT) / self.GRID_SIZE)
        self.obstacle_pos = [
            [False for i in range(self._y_width)] for i in range(self._x_width)
        ]
        self.__create_obstacle_map(x_obstacle, y_obstacle)

    @staticmethod
    def __calc_heuristic(num1, num2):
        weight = 3.0
        return weight * (abs(num1.x - num2.x) ** 2 + abs(num1.y - num2.y) ** 2) ** 0.5

    def __calc_grid_position(self, idx, p):
        return idx * self.GRID_SIZE + p

    def __calc_xy(self, position, min_position):
        return round((position - min_position) / self.GRID_SIZE)

    def __calc_grid_idx(self, node):
        return (node.y) * self._x_width + (node.x)

    def __check_validity(self, node):
        x_position = self.__calc_grid_position(node.x, 0)
        y_position = self.__calc_grid_position(node.y, 0)

        if x_position < 0:
            return False
        elif y_position < 0:
            return False
        elif x_position >= self.WIDTH:
            return False
        elif y_position >= self.HEIGHT:
            return False
        if self.obstacle_pos[node.x][node.y]:
            return False
        return True

    def add_obstacles(self, obstacles: List[GameObject]):
        x_obstacle = [x for x, _ in obstacles]
        y_obstacle = [y for _, y in obstacles]
        self.__create_obstacle_map(x_obstacle, y_obstacle)

    def __create_obstacle_map(self, x_obstacle, y_obstacle):
        DELTA = ceil(self.ROBOT_RADIUS / self.GRID_SIZE) + 3

        for idx_x_obstacle, idx_y_obstacle in zip(x_obstacle, y_obstacle):
            x_norm = int(idx_x_obstacle // self.GRID_SIZE)
            y_norm = int(idx_y_obstacle // self.GRID_SIZE)
            for idx_x in range(x_norm - DELTA, x_norm + DELTA):
                x = self.__calc_grid_position(idx_x, 0)
                if not (0 <= idx_x < self._x_width):
                    continue
                for idx_y in range(y_norm - DELTA, y_norm + DELTA):
                    if not (0 <= idx_y < self._y_width):
                        continue
                    y = self.__calc_grid_position(idx_y, 0)
                    d = math.sqrt((idx_x_obstacle - x) ** 2 + (idx_y_obstacle - y) ** 2)
                    if d <= self.ROBOT_RADIUS:
                        self.obstacle_pos[idx_x][idx_y] = True
        if self._show_animation:
            plt.plot(x_obstacle, y_obstacle, ".k")
            plt.grid(True)
            plt.axis("equal")

    @staticmethod
    def __get_path():
        path = [
            [1, 0, 1],
            [0, 1, 1],
            [-1, 0, 1],
            [0, -1, 1],
            # [-1, -1, math.sqrt(2)],
            # [-1, 1, math.sqrt(2)],
            # [1, -1, math.sqrt(2)],
            # [1, 1, math.sqrt(2)],
        ]

        return path

    def __calc_final_path(self, end_node, record_closed):
        x_out_path, y_out_path = [self.__calc_grid_position(end_node.x, 0)], [
            self.__calc_grid_position(end_node.y, 0)
        ]
        path = end_node.path
        while path != -1:
            prev_node = record_closed[self.__calc_grid_idx(path)]
            x_out_path.append(self.__calc_grid_position(prev_node.x, 0))
            y_out_path.append(self.__calc_grid_position(prev_node.y, 0))
            path = prev_node.path

        return x_out_path, y_out_path

    def search_closest_path(
        self, start: GameObject, end: GameObject
    ) -> List[Tuple[int, int]]:
        start_x, start_y = map(int, (start.x, start.y))
        end_x, end_y = map(int, (end.x, end.y))

        start_node = Node(
            self.__calc_xy(start_x, 0),
            self.__calc_xy(start_y, 0),
            0.0,
            -1,
        )
        start_node.cost = 0

        end_node = Node(
            self.__calc_xy(end_x, 0),
            self.__calc_xy(end_y, 0),
            0.0,
            -1,
        )

        record_open, record_closed = dict(), dict()
        record_open[self.__calc_grid_idx(start_node)] = start_node
        state = _PriorityQueue()
        state.put(start_node, start_node.cost)

        while True:
            print(state.elements)
            if len(state.elements) == 0:
                print("Check Record Validity")
                break

            closest_node = state.get()
            if self.__calc_grid_idx(closest_node) in record_closed:
                continue
            if self._show_animation:  # pragma: no cover
                plt.plot(
                    self.__calc_grid_position(closest_node.x, 0),
                    self.__calc_grid_position(closest_node.y, 0),
                    "xy",
                )
                if len(record_closed.keys()) % 10 == 0:
                    plt.pause(0.001)

            if closest_node.x == end_node.x and closest_node.y == end_node.y:
                print("Finished!")
                end_node.path = closest_node.path
                end_node.cost = closest_node.cost
                break

            record_closed[self.__calc_grid_idx(closest_node)] = closest_node

            for i, _ in enumerate(self._path):
                next_node = Node(
                    closest_node.x + self._path[i][0],
                    closest_node.y + self._path[i][1],
                    0,
                    closest_node,
                )
                next_node.cost = (
                    closest_node.cost
                    - self.__calc_heuristic(closest_node, end_node)
                    + self._path[i][2]
                    + self.__calc_heuristic(next_node, end_node)
                )

                idx_node = self.__calc_grid_idx(next_node)
                if not self.__check_validity(next_node):
                    continue

                if idx_node in record_closed:
                    continue

                if idx_node not in record_open:
                    record_open[idx_node] = next_node
                    state.put(next_node, next_node.cost)
                else:
                    if record_open[idx_node].cost > next_node.cost:
                        record_open[idx_node] = next_node
                        state.put(next_node, next_node.cost)

        x_out_path, y_out_path = self.__calc_final_path(end_node, record_closed)
        print([(x, y) for x, y in zip(x_out_path, y_out_path)])
        approx_path = _transform_path(x_out_path, y_out_path)
        if self._show_animation:
            x_out_path = []
            y_out_path = []
            for point in approx_path:
                x_out_path.append(point[0][0])
                y_out_path.append(point[0][1])
            print(x_out_path, y_out_path)
            plt.plot(x_out_path, y_out_path, "r")
            plt.show()
        return approx_path


def _gen_points() -> Tuple[GameObject, GameObject]:
    start = GameObject(100, 100)
    end = GameObject(300, 300)
    return start, end


def _gen_obstacles(lower: int, upper: int) -> List[Tuple[int, int]]:
    obstacles = [(1, 1), (320, 320)]
    for x in range(lower, upper):
        for y in range(lower, upper):
            obstacles.append((x, y))
    return obstacles


def main():
    # camera = TopCamera("rtsp://Admin:rtf123@192.168.2.251:554/1", 'detecting_objects-ygnzn/1', api_key="d6bnjs5HORwCF1APwuBX")
    start, end = _gen_points()
    obstacles = _gen_obstacles(150, 250)

    a_star: AStarSearcher = AStarSearcher(obstacles)
    
    obstacles = _gen_obstacles(270, 290)
    a_star.add_obstacles(obstacles)
    
    path: List[Tuple[int, int]] = a_star.search_closest_path(start, end)

    print(path)


if __name__ == "__main__":
    main()
