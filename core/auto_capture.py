import threading
import time
from core.camera import take_photo
from core.config_state import get_config, save_config

def loop():
    taken_photos = 0
    last_burst_time = 0

    while True:
        config = get_config()

        if config['enabled']:
            max_photos = config.get('max_photos', 0)
            interval = config.get('interval', 10)
            led_auto = config.get('led_auto', True)
            led_enabled = config.get('led_enabled', True)

            burst_mode = not led_enabled and not led_auto

            if max_photos == 0:
                print("[AUTO] Tomando foto automática...")
                take_photo()
                time.sleep(interval)

            elif burst_mode:
                now = time.time()
                if now - last_burst_time >= interval:
                    print(f"[AUTO] Tomando {max_photos} fotos en ráfaga...")
                    for _ in range(max_photos):
                        take_photo()
                    last_burst_time = now
                else:
                    time.sleep(1)

            else:
                if taken_photos < max_photos:
                    print("[AUTO] Tomando foto automática...")
                    take_photo()
                    taken_photos += 1
                    time.sleep(interval)
                else:
                    print("[AUTO] Límite de fotos alcanzado. Deteniendo captura automática.")
                    config['enabled'] = False
                    save_config(config)
        else:
            taken_photos = 0
            last_burst_time = 0
            time.sleep(1)


def start_auto_capture():
    t = threading.Thread(target=loop, daemon=True)
    t.start()
