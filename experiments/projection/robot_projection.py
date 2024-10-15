import time

import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt


img = cv.imread('proj_photo_1.jpg')
assert img is not None, "file could not be read, check with os.path.exists()"
rows, cols, ch = img.shape

# Define source and destination points
srcPoints = np.array([[320, 478], [638, 449], [320, 147], [502, 149]], dtype=np.float32)
dstPoints = np.array([[200*3, 1000*3], [305*3, (1000-10)*3], [3*200, (1000-290)*3], [305*3, (1000-290)*3]], dtype=np.float32)

# Compute homography matrix
M, mask = cv.findHomography(srcPoints, dstPoints, cv.RANSAC, 5.0)
start = time.time()
dst = cv.warpPerspective(img,M,(400*3, 1000*3))
end = time.time()

print(end - start)
plt.imshow(dst)
plt.show()