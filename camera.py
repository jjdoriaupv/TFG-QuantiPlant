import cv2
from datetime import datetime
import os

def take_photo():
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    cam.release()
    if not ret:
        return None

    if not os.path.exists("static"):
        os.makedirs("static")

    filename = f"static/photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    cv2.imwrite(filename, frame)
    return filename
