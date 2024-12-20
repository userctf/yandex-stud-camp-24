import cv2
import heapq
from time import time
import math
from math import floor, ceil
import matplotlib.pyplot as plt
import numpy as np

show_animation = True


class PriorityQueue:
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
        return str(self.x) + '+' + str(self.y) + ',' + str(self.cost) + ',' + str(self.path)


class AStarPath:
    def __init__(self, robot_radius, grid_size, x_obstacle, y_obstacle):
        self.grid_size = grid_size
        self.robot_radius = robot_radius
        self.create_obstacle_map(x_obstacle, y_obstacle)
        self.path = self.get_path()

    @staticmethod
    def calc_heuristic(num1, num2):
        weight = 3.0
        return weight * (abs(num1.x - num2.x) + abs(num1.y - num2.y))

    def calc_grid_position(self, idx, p):
        return idx * self.grid_size + p

    def calc_xy(self, position, min_position):
        return round((position - min_position) / self.grid_size)

    def calc_grid_idx(self, node):
        return (node.y - self.y_min) * self.x_width + (node.x - self.x_min)

    def check_validity(self, node):
        x_position = self.calc_grid_position(node.x, self.x_min)
        y_position = self.calc_grid_position(node.y, self.y_min)

        if x_position < self.x_min:
            return False
        elif y_position < self.y_min:
            return False
        elif x_position >= self.x_max:
            return False
        elif y_position >= self.y_max:
            return False
        if self.obstacle_pos[node.x][node.y]:
            return False
        return True

    def create_obstacle_map(self, x_obstacle, y_obstacle):
        self.x_min = round(min(x_obstacle))
        self.y_min = round(min(y_obstacle))
        self.x_max = round(max(x_obstacle))
        self.y_max = round(max(y_obstacle))
        self.x_width = round((self.x_max - self.x_min) / self.grid_size)
        self.y_width = round((self.y_max - self.y_min) / self.grid_size)
        self.obstacle_pos = [[False for i in range(self.y_width)] for i in range(self.x_width)]
        DELTA = ceil(self.robot_radius / self.grid_size) + 3

        for idx_x_obstacle, idx_y_obstacle in zip(x_obstacle, y_obstacle):
            x_norm = int((idx_x_obstacle - self.x_min) // self.grid_size)
            y_norm = int((idx_y_obstacle - self.y_min) // self.grid_size)
            for idx_x in range(x_norm - DELTA, x_norm + DELTA):
                x = self.calc_grid_position(idx_x, self.x_min)
                if (not (0 <= idx_x < self.x_width)):
                    continue
                for idx_y in range(y_norm - DELTA, y_norm + DELTA):
                    if not (0 <= idx_y < self.y_width):
                        continue
                    y = self.calc_grid_position(idx_y, self.y_min)
                    d = math.sqrt((idx_x_obstacle - x) ** 2 + (idx_y_obstacle - y) ** 2)
                    if d <= self.robot_radius:
                        self.obstacle_pos[idx_x][idx_y] = True

    @staticmethod
    def get_path():
        path = [[1, 0, 1],
                [0, 1, 1],
                [-1, 0, 1],
                [0, -1, 1],
                [-1, -1, math.sqrt(2)],
                [-1, 1, math.sqrt(2)],
                [1, -1, math.sqrt(2)],
                [1, 1, math.sqrt(2)]]

        return path

    def calc_final_path(self, end_node, record_closed):
        x_out_path, y_out_path = [self.calc_grid_position(end_node.x, self.x_min)], [
            self.calc_grid_position(end_node.y, self.y_min)]
        path = end_node.path
        while path != -1:
            prev_node = record_closed[self.calc_grid_idx(path)]
            x_out_path.append(self.calc_grid_position(prev_node.x, self.x_min))
            y_out_path.append(self.calc_grid_position(prev_node.y, self.y_min))
            path = prev_node.path

        return x_out_path, y_out_path

    def a_star_search(self, start_x, start_y, end_x, end_y):
        end_node = Node(self.calc_xy(end_x, self.x_min), self.calc_xy(end_y, self.y_min), 0.0, -1)
        start_node = Node(self.calc_xy(start_x, self.x_min), self.calc_xy(start_y, self.y_min), 0.0, -1)
        start_node.cost = 0

        record_open, record_closed = dict(), dict()
        record_open[self.calc_grid_idx(start_node)] = start_node
        state = PriorityQueue()
        state.put(start_node, start_node.cost)

        while True:
            if len(state.elements) == 0:
                print('Check Record Validity')
                break

            closest_node = state.get()
            if self.calc_grid_idx(closest_node) in record_closed:
                continue
            if show_animation:  # pragma: no cover
                plt.plot(self.calc_grid_position(closest_node.x, self.x_min),
                         self.calc_grid_position(closest_node.y, self.y_min), "xy")
                if len(record_closed.keys()) % 10 == 0:
                    plt.pause(0.001)

            if closest_node.x == end_node.x and closest_node.y == end_node.y:
                print("Finished!")
                end_node.path = closest_node.path
                end_node.cost = closest_node.cost
                break

            record_closed[self.calc_grid_idx(closest_node)] = closest_node

            for i, _ in enumerate(self.path):
                next_node = Node(closest_node.x + self.path[i][0], closest_node.y + self.path[i][1],
                                 0, closest_node)
                next_node.cost = closest_node.cost - self.calc_heuristic(closest_node, end_node) + self.path[i][
                    2] + self.calc_heuristic(next_node, end_node)

                idx_node = self.calc_grid_idx(next_node)
                if not self.check_validity(next_node):
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

        x_out_path, y_out_path = self.calc_final_path(end_node, record_closed)

        return x_out_path, y_out_path


def main():
    start_x = 30
    start_y = 20
    end_x = 165
    end_y = 140
    grid_size = 4.0
    robot_radius = 5.0

    image = cv2.imread('img.png')
    y, x, _ = image.shape
    image = image[:, 250:x - 400]
    image = cv2.resize(image, (200, 155))

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    lower_red1 = np.array([0, 50, 50])  # Первый диапазон красного
    upper_red1 = np.array([10, 255, 255])

    lower_red2 = np.array([170, 50, 50])  # Второй диапазон красного
    upper_red2 = np.array([180, 255, 255])

    lower_green = np.array([50, 100, 100])
    upper_green = np.array([85, 255, 255])

    # Создаем маски для обоих диапазонов красного
    green_mask = cv2.inRange(hsv, lower_green, upper_green)
    mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)

    # Объединяем две маски в одну
    mask = mask_red1 | mask_red2 | green_mask
    image[mask != 0] = [255, 255, 255]


    cv2.imshow("h", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    lower_black = np.array([0, 0, 0])  # Нижний порог
    upper_black = np.array([180, 255, 50])  # Верхний порог для черных объектов
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # Применение маски для выделения темных объектов
    mask = cv2.inRange(hsv_image, lower_black, upper_black)

    width, length = mask.shape
    cv2.imshow("h", mask)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    x_obstacle, y_obstacle = [], []
    for i in range(width):
        for j in range(length):
            if mask[i][j] == 255:
                y_obstacle.append(i)
                x_obstacle.append(j)

    if show_animation:
        plt.plot(x_obstacle, y_obstacle, ".k")
        plt.plot(start_x, start_y, "og")
        plt.plot(end_x, end_y, "xb")
        plt.grid(True)
        plt.axis("equal")
    slow = time()
    a_star = AStarPath(robot_radius, grid_size, x_obstacle, y_obstacle)
    print(f"Init time:", time() - slow)
    start = time()
    x_out_path, y_out_path = a_star.a_star_search(start_x, start_y, end_x, end_y)
    print(f"Search time:", time() - start)

    if show_animation:
        plt.plot(x_out_path, y_out_path, "r")
        plt.show()


if __name__ == '__main__':
    main()
