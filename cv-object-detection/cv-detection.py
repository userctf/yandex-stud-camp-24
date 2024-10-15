import cv2


url = "http://192.168.2.106:8080/?action=stream"

class CVDetection:
    def __init__(self, url: str):
        self.cap = cv2.VideoCapture(url)

    def get_frame(self):
        print("zashli")
        while True:
            ret, frame = self.cap.read()
            print(frame.shape)
            if not ret:
                print("Error while reading frame")
            cv2.imshow("frame", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    def __del__(self):
        self.cap.release()
        cv2.destroyAllWindows()

model = CVDetection(url)
model.get_frame()