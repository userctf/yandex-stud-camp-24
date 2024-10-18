import cv2
import time
import os
import sys


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../modules')))
from modules.top_camera import TopCamera
from modules.base_camera import ObjectType

camera = TopCamera("rtsp://Admin:rtf123@192.168.2.250:554/1", 'detecting_objects-ygnzn/1',
                   api_key="d6bnjs5HORwCF1APwuBX")

image = cv2.imread("left.jpg")
preds = camera.predict(image)
print(preds)