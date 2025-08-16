import threading
import time
from core.camera import take_photo
from core.config_state import get_config, save_config

_worker = None
_worker_lock = threading.Lock()

def loop():
    session_active = False
    photos_taken = 0
    next_due = None
    last_burst_time = 0.0
    burst_intervals_done = 0

    while True:
        config = get_config()
        enabled = config.get('enabled', False)

        if enabled and not session_active:
            session_active = True
            photos_taken = -1
            next_due = time.monotonic()
            last_burst_time = 0.0
            burst_intervals_done = 0
            cfg = get_config()
            cfg['photos_taken'] = 0
            save_config(cfg)

        if enabled:
            cfg = get_config()
            burst_mode_enabled = cfg.get('burst_mode_enabled', False)

            if burst_mode_enabled:
                max_intervals = cfg.get('max_intervals', 0)
                burst_count = cfg.get('burst_count', 0)
                interval_between_bursts = cfg.get('interval_between_bursts', 3600)
                burst_interval = cfg.get('burst_interval', 60)

                now = time.monotonic()
                if (max_intervals == 0 or burst_intervals_done < max_intervals) and (last_burst_time == 0.0 or now - last_burst_time >= interval_between_bursts):
                    for i in range(burst_count):
                        take_photo()
                        if i < burst_count - 1:
                            time.sleep(burst_interval)
                    burst_intervals_done += 1
                    last_burst_time = time.monotonic()
                elif max_intervals > 0 and burst_intervals_done >= max_intervals:
                    cfg = get_config()
                    cfg['enabled'] = False
                    save_config(cfg)
                else:
                    time.sleep(0.5)
            else:
                max_photos = int(cfg.get('max_photos', 0))
                interval_sec = max(1, int(cfg.get('interval', 10)))
                now = time.monotonic()

                if max_photos == 0:
                    if next_due is None or now >= next_due:
                        take_photo()
                        next_due = now + interval_sec
                    else:
                        time.sleep(min(1.0, max(0.0, next_due - now)))
                else:
                    if photos_taken >= max_photos:
                        cfg = get_config()
                        cfg['enabled'] = False
                        cfg['photos_taken'] = 0
                        save_config(cfg)
                        session_active = False
                        photos_taken = 0
                        next_due = None
                        time.sleep(0.5)
                        continue

                    if next_due is None or now >= next_due:
                        take_photo()
                        photos_taken += 1
                        cfg = get_config()
                        cfg['photos_taken'] = photos_taken
                        save_config(cfg)
                        next_due = now + interval_sec
                    else:
                        time.sleep(min(1.0, max(0.0, next_due - now)))
        else:
            if session_active:
                session_active = False
                photos_taken = 0
                next_due = None
                last_burst_time = 0.0
                burst_intervals_done = 0
                cfg = get_config()
                cfg['photos_taken'] = 0
                save_config(cfg)
            time.sleep(0.5)

def start_auto_capture():
    global _worker
    with _worker_lock:
        if _worker is not None and _worker.is_alive():
            return
        _worker = threading.Thread(target=loop, daemon=True)
        _worker.start()
