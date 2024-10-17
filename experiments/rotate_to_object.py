import math


def rotate_to_object(x_obj: int, y_obj: int) -> int:
    # coord of rotate center of robot
    x_center = 35
    y_center = -140

    lenght = math.sqrt((x_obj - x_center)**2 + (y_obj - y_center)**2)
    gamma = math.asin(abs(x_center) / lenght)
    alpha = math.atan2(x_obj - x_center, y_obj - y_center)
    rotate_angle = alpha + gamma

    return int(rotate_angle * 180 / math.pi + 0.5)


# y = int(150 * 3**0.5 + 35 / 2 - 140)
# x = int(150 + 35 - (35 / 2) * 3**0.5)
x = 2000
y = -140 + 35
print(rotate_to_object(x, y))
