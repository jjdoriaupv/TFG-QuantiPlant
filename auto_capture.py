import threading
import time
from camera import take_photo

capture_enabled = False
capture_interval = 10
capture_lock = threading.Lock()

def start_auto_capture():
    def loop():
        while True:
            with capture_lock:
                enabled = capture_enabled
                interval = capture_interval
            if enabled:
                print("[AutoCapture] Tomando foto automática...")
                take_photo()
            time.sleep(interval)
    t = threading.Thread(target=loop, daemon=True)
    t.start()

def enable_capture(enable: bool):
    global capture_enabled
    with capture_lock:
        capture_enabled = enable

def set_interval(seconds: int):
    global capture_interval
    with capture_lock:
        capture_interval = seconds

def get_config():
    with capture_lock:
        return {"enabled": capture_enabled, "interval": capture_interval}
