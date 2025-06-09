import threading
import time
from camera import take_photo

capture_enabled = False
capture_interval = 10


def start_auto_capture():
    def loop():
        while True:
            if capture_enabled:
                take_photo()
            time.sleep(capture_interval)

    t = threading.Thread(target=loop, daemon=True)
    t.start()

def enable_capture(enable):
    global capture_enabled
    capture_enabled = enable

def set_interval(seconds):
    global capture_interval
    capture_interval = seconds