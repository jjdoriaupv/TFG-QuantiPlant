import threading
import time
from camera import take_photo
from config_state import config

def loop():
    while True:
        if config['enabled']:
            print("[AUTO] Tomando foto automática...")
            take_photo()
            time.sleep(config['interval'])
        else:
            time.sleep(1)

def start_auto_capture():
    t = threading.Thread(target=loop, daemon=True)
    t.start()

