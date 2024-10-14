import math


# в миллиметрах
l1 = 90
l2 = 165
x = 165 + 90
y = 0
Q1 = math.atan(y / x) + math.acos((l1**2 + x**2 + y**2 - l2**2) / (2 * l1 * (x**2 + y**2)**0.5))
Q2 = math.pi - math.acos((l1**2 + l2**2 - x**2 - y**2) / (2 * l1 * l2))
alpha = 70 + Q1
betta = 170 - Q2

print(alpha)
print(betta)
