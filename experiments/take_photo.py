import cv2
import time
import os

def take_photo(url, photo_id):
    video_stream = cv2.VideoCapture(url) 

    # time_position = 10 
    # video_stream.set(cv2.CAP_PROP_POS_MSEC, time_position * 1000)
    # video_stream.release()
    success, frame = video_stream.read()

    if success:
        cv2.imwrite(f"./photos/captured_frame_{photo_id}.jpg", frame)
    else:
        print("Can't save photo")

cmd = input()
# os.mkdir("./photos")
while cmd == "":
    print("new one")
    take_photo("http://192.168.2.106:8080/?action=stream", time.time())
    cmd = input()