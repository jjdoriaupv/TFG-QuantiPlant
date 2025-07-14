import threading
import time
from core.camera import take_photo
from core.config_state import get_config

def loop():
    taken_photos = 0
    while True:
        config = get_config()
        if config['enabled']:
            max_photos = config.get('max_photos', 0)
            if max_photos == 0 or taken_photos < max_photos:
                print("[AUTO] Tomando foto automática...")
                take_photo()
                taken_photos += 1
                time.sleep(config['interval'])
            else:
                print("[AUTO] Límite de fotos alcanzado. Deteniendo captura automática.")
                config['enabled'] = False
                save_config(config)
        else:
            taken_photos = 0
            time.sleep(1)


def start_auto_capture():
    t = threading.Thread(target=loop, daemon=True)
    t.start()
