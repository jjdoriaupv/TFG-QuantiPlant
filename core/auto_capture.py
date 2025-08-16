import threading
import time
from core.camera import take_photo
from core.config_state import get_config, save_config

_state_lock = threading.Lock()
_worker = None
_worker_lock = threading.Lock()

def loop():
    last_burst_time = 0.0
    burst_intervals_done = 0
    session_active = False
    next_due = None

    while True:
        with _state_lock:
            config = get_config()
            enabled = config.get('enabled', False)

        if enabled and not session_active:
            session_active = True
            last_burst_time = 0.0
            burst_intervals_done = 0
            next_due = 0.0
            with _state_lock:
                cfg = get_config()
                cfg['photos_taken'] = 0
                save_config(cfg)

        if enabled:
            with _state_lock:
                config = get_config()
            burst_mode_enabled = config.get('burst_mode_enabled', False)

            if burst_mode_enabled:
                max_intervals = config.get('max_intervals', 0)
                burst_count = config.get('burst_count', 0)
                interval_between_bursts = config.get('interval_between_bursts', 3600)
                burst_interval = config.get('burst_interval', 60)

                now = time.monotonic()
                if burst_intervals_done < max_intervals and (last_burst_time == 0.0 or now - last_burst_time >= interval_between_bursts):
                    for i in range(burst_count):
                        take_photo()
                        if i < burst_count - 1:
                            time.sleep(burst_interval)
                    burst_intervals_done += 1
                    last_burst_time = time.monotonic()
                elif burst_intervals_done >= max_intervals:
                    with _state_lock:
                        cfg = get_config()
                        cfg['enabled'] = False
                        save_config(cfg)
                else:
                    time.sleep(0.5)
            else:
                max_photos = config.get('max_photos', 0)
                interval_sec = max(1, int(config.get('interval', 10)))
                led_auto = config.get('led_auto', True)
                led_enabled = config.get('led_enabled', True)
                burst_mode = not led_enabled and not led_auto
                now = time.monotonic()

                if max_photos == 0:
                    if next_due is None or now >= next_due:
                        take_photo()
                        next_due = now + interval_sec
                    else:
                        time.sleep(min(1.0, max(0.0, next_due - now)))
                elif burst_mode:
                    if last_burst_time == 0.0 or now - last_burst_time >= interval_sec:
                        exposure = config.get('exposure', 1000000)
                        delay = (exposure / 1_000_000.0) + 5.0
                        for _ in range(max_photos):
                            take_photo()
                            time.sleep(delay)
                        last_burst_time = time.monotonic()
                        with _state_lock:
                            cfg = get_config()
                            cfg['enabled'] = False
                            save_config(cfg)
                    else:
                        time.sleep(0.5)
                else:
                    with _state_lock:
                        photos_taken = get_config().get('photos_taken', 0)
                    if photos_taken >= max_photos:
                        with _state_lock:
                            cfg = get_config()
                            cfg['enabled'] = False
                            save_config(cfg)
                        continue
                    if next_due is None:
                        next_due = 0.0
                    if now >= next_due:
                        take_photo()
                        with _state_lock:
                            cfg = get_config()
                            cfg['photos_taken'] = cfg.get('photos_taken', 0) + 1
                            save_config(cfg)
                        if cfg['photos_taken'] >= max_photos:
                            with _state_lock:
                                cfg = get_config()
                                cfg['enabled'] = False
                                save_config(cfg)
                        else:
                            next_due = now + interval_sec
                    else:
                        time.sleep(min(1.0, max(0.0, next_due - now)))
        else:
            if session_active:
                session_active = False
                last_burst_time = 0.0
                burst_intervals_done = 0
                next_due = None
            time.sleep(1)

def start_auto_capture():
    global _worker
    with _worker_lock:
        if _worker is not None and _worker.is_alive():
            return
        _worker = threading.Thread(target=loop, daemon=True)
        _worker.start()
