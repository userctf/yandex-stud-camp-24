import time

import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt


img = cv.imread('image_robot.jpg')
assert img is not None, "file could not be read, check with os.path.exists()"
rows, cols, ch = img.shape

# Define source and destination points
srcPoints = np.array([[34, 959], [300, 522], [661, 522], [852, 959]], dtype=np.float32)
dstPoints = np.array([[0, 600*3], [0, 0], [500*3, 0], [500*3, 600*3]], dtype=np.float32)

# Compute homography matrix
M, mask = cv.findHomography(srcPoints, dstPoints, cv.RANSAC, 5.0)
start = time.time()
dst = cv.warpPerspective(img,M,(500*3,600*3))
end = time.time()

print(end - start)
plt.imshow(dst)
plt.show()