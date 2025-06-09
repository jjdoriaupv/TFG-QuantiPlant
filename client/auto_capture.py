import threading
import time
from camera import take_photo

config = {
    'enabled': False,
    'interval': 10
}

def loop():
    while True:
        if config['enabled']:
            print("[AUTO] Tomando foto automática...")
            take_photo()
        time.sleep(config['interval'])

def start_auto_capture():
    t = threading.Thread(target=loop, daemon=True)
    t.start()

def enable_capture(enabled):
    config['enabled'] = enabled

def set_interval(interval):
    config['interval'] = interval

def get_config():
    return config
