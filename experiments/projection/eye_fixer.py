from __future__ import print_function
import numpy as np
import cv2
import glob
from matplotlib import pyplot as plt
import os

img_names_undistort = [img for img in glob.glob("top_images/*.png")]
new_path = "/Users/rattysed/PycharmProjects/yandex-stud-camp-24/experiments/projection/out/"

camera_matrix = np.array([[798.35968226, 0., 952.86158649],
                          [0., 799.1283211, 584.42288843],
                          [0., 0., 1.]])
dist_coefs = np.array([-0.23619838, 0.18406916, 0.00527998, -0.00473346, -0.09061932])

i = 0

# for img_found in img_names_undistort:
while i < len(img_names_undistort):
    img = cv2.imread(img_names_undistort[i])
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    h, w = img.shape[:2]
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, dist_coefs, (w, h), 1, (w, h))

    dst = cv2.undistort(img, camera_matrix, dist_coefs, None, newcameramtx)

    dst = cv2.cvtColor(dst, cv2.COLOR_BGR2RGB)

    # crop and save the image
    x, y, w, h = roi
    dst = dst[y:y + h, x:x + w]

    name = img_names_undistort[i].split("/")
    name = name[-1].split(".")
    name = name[0]
    full_name = new_path + name + '.jpg'

    # outfile = img_names_undistort + '_undistorte.png'
    print('Undistorted image written to: %s' % full_name)
    cv2.imwrite(full_name, dst)
    i = i + 1
