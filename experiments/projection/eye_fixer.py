from __future__ import print_function

import numpy as np
import cv2
import glob
from matplotlib import pyplot as plt
import os

img_names_undistort = [img for img in glob.glob("top_images/lc*.png")]
new_path = "/Users/rattysed/PycharmProjects/yandex-stud-camp-24/experiments/projection/out/"

# camera_matrix = np.array([[713.055456, 0., 936.55387964],
#                           [0., 714.19333345, 594.33880656],
#                           [0., 0., 1., ]])
# dist_coefs = np.array([-0.15776208, 0.05862795, 0.00185709, -0.00275354, -0.01768117])

right_matrix = np.array([[2.95403994e+03, 0.00000000e+00, 9.39499550e+02],
                         [0.00000000e+00, 2.60512675e+03, 5.34861500e+02],
                         [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
right_dist_coefs = np.array([-1.52724225, 2.07633978, 0.08809736, -0.01248329, 3.83043747])

right_matrix2 = np.array([[1.18449525e+03, 0.00000000e+00, 8.75567971e+02],
                          [0.00000000e+00, 1.19039897e+03, 6.09741970e+02],
                          [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])
right_dist_coefs2 = np.array([-4.55959959e-01, 4.01401480e-01, 2.89769234e-04, 6.00998076e-03,
                              -2.61647942e-01])

right_matrix3 = np.array([[1182.719, 0., 927.03],
                          [0., 1186.236, 609.52],
                          [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])

right_dist_coefs3 = np.array([-0.5, 0.3, 0, 0, 0])

left_matrix = np.array([[850.07, 0., 929.22],
                        [0., 846.76, 575.28],
                        [0., 0., 1.]])

left_dist_coefs = np.array([-0.2, 0.05, 0, 0, 0])
camera_matrix = left_matrix
dist_coefs = left_dist_coefs

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
    dst = dst[y - 20:y + h, x:x + w]

    name = img_names_undistort[i].split("/")
    name = name[-1].split(".")
    name = name[0]
    full_name = new_path + name + '.jpg'

    # outfile = img_names_undistort + '_undistorte.png'
    print('Undistorted image written to: %s' % full_name)
    cv2.imwrite(full_name, dst)
    i = i + 1
