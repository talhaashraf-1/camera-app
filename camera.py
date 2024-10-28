import cv2
from PIL import Image, ImageTk

class Camera:
    def __init__(self, video_source=0):
        self.vid = cv2.VideoCapture(video_source)

    def get_frame(self):
        ret, frame = self.vid.read()
        if ret:
            return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return None

    def release(self):
        if self.vid.isOpened():
            self.vid.release()