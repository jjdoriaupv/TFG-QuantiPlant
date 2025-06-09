import threading
import time
from camera import take_photo

# Configuración compartida
config = {
    'enabled': False,
    'interval': 10,       # en segundos
    'exposure': 1000      # en milisegundos
}

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

def enable_capture(enabled):
    config['enabled'] = enabled

def set_interval(interval):
    config['interval'] = interval

def set_exposure(exposure):
    config['exposure'] = exposure

def get_config():
    return config
