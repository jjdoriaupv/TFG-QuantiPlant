import threading
import time
from core.camera import take_photo
from core.config_state import get_config, save_config

def loop():
    taken_photos = 0
    last_burst_time = 0
    burst_intervals_done = 0

    while True:
        config = get_config()

        if config.get('enabled', False):
            burst_mode_enabled = config.get('burst_mode_enabled', False)

            if burst_mode_enabled:
                max_intervals = config.get('max_intervals', 0)
                burst_count = config.get('burst_count', 0)
                interval_between_bursts = config.get('interval_between_bursts', 3600)
                burst_interval = config.get('burst_interval', 60)

                now = time.time()
                if burst_intervals_done < max_intervals and now - last_burst_time >= interval_between_bursts:
                    for i in range(burst_count):
                        take_photo()
                        if i < burst_count - 1:
                            time.sleep(burst_interval)
                    burst_intervals_done += 1
                    last_burst_time = time.time()
                elif burst_intervals_done >= max_intervals:
                    config['enabled'] = False
                    save_config(config)
                else:
                    time.sleep(1)

            else:
                max_photos = config.get('max_photos', 0)
                interval = config.get('interval', 10)
                led_auto = config.get('led_auto', True)
                led_enabled = config.get('led_enabled', True)

                burst_mode = not led_enabled and not led_auto

                if max_photos == 0:
                    take_photo()
                    time.sleep(interval)

                elif burst_mode:
                    now = time.time()
                    if now - last_burst_time >= interval:
                        exposure = config.get('exposure', 1000000)
                        delay = (exposure / 1_000_000.0) + 5.0
                        for i in range(max_photos):
                            take_photo()
                            if i < max_photos - 1:
                                time.sleep(delay)
                        last_burst_time = time.time()
                    else:
                        time.sleep(1)
                else:
                    if taken_photos < max_photos:
                        take_photo()
                        taken_photos += 1
                        time.sleep(interval)
                    else:
                        config['enabled'] = False
                        save_config(config)
        else:
            taken_photos = 0
            last_burst_time = 0
            burst_intervals_done = 0
            time.sleep(1)

def start_auto_capture():
    t = threading.Thread(target=loop, daemon=True)
    t.start()
