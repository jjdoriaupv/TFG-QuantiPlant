import threading
import time
from camera import take_photo
from config_state import get_config

def loop():
    while True:
        config = get_config()
        if config['enabled']:
            print("[AUTO] Tomando foto automática...")
            take_photo()
            time.sleep(config['interval'])
        else:
            time.sleep(1)

def start_auto_capture():
    t = threading.Thread(target=loop, daemon=True)
    t.start()
