import threading
import time
from core.camera import take_photo
from core.config_state import get_config, save_config

_worker = None
_worker_lock = threading.Lock()

def _update_config(**kv):
    cfg = get_config()
    for k, v in kv.items():
        cfg[k] = v
    save_config(cfg)

def loop():
    session_active = False
    photos_taken = 0
    next_due = None
    last_burst_time = 0.0
    burst_intervals_done = 0

    while True:
        cfg = get_config()
        enabled = cfg.get('enabled', False)

        if enabled and not session_active:
            session_active = True
            photos_taken = 0
            next_due = time.monotonic()
            last_burst_time = 0.0
            burst_intervals_done = 0
            max_photos = int(cfg.get('max_photos', 0))
            interval_sec = max(1, int(cfg.get('interval', 10)))
            _update_config(
                photos_taken=0,
                remaining_photos=(max_photos if max_photos > 0 else None),
                next_shot_epoch=float(time.time() + (0 if max_photos == 0 else 0))
            )

        if enabled:
            cfg = get_config()
            burst_mode_enabled = cfg.get('burst_mode_enabled', False)

            if burst_mode_enabled:
                max_intervals = int(cfg.get('max_intervals', 0))
                burst_count = int(cfg.get('burst_count', 0))
                interval_between_bursts = int(cfg.get('interval_between_bursts', 3600))
                burst_interval = int(cfg.get('burst_interval', 60))

                now_mono = time.monotonic()

                if (max_intervals == 0 or burst_intervals_done < max_intervals) and (last_burst_time == 0.0 or now_mono - last_burst_time >= interval_between_bursts):
                    for i in range(burst_count):
                        take_photo()
                        if i < burst_count - 1:
                            _update_config(next_shot_epoch=float(time.time() + burst_interval), remaining_photos=None)
                            time.sleep(burst_interval)
                    burst_intervals_done += 1
                    last_burst_time = time.monotonic()
                    _update_config(next_shot_epoch=float(time.time() + interval_between_bursts), remaining_photos=None)
                elif max_intervals > 0 and burst_intervals_done >= max_intervals:
                    _update_config(enabled=False, photos_taken=0, remaining_photos=0, next_shot_epoch=None)
                else:
                    eta = (last_burst_time + interval_between_bursts) - now_mono if last_burst_time != 0.0 else 0
                    _update_config(next_shot_epoch=float(time.time() + max(0, eta)), remaining_photos=None)
                    time.sleep(0.5)
            else:
                max_photos = int(cfg.get('max_photos', 0))
                interval_sec = max(1, int(cfg.get('interval', 10)))
                now_mono = time.monotonic()

                if max_photos == 0:
                    if next_due is None or now_mono >= next_due:
                        take_photo()
                        next_due = now_mono + interval_sec
                        _update_config(next_shot_epoch=float(time.time() + interval_sec), remaining_photos=None)
                    else:
                        _update_config(next_shot_epoch=float(time.time() + max(0, next_due - now_mono)), remaining_photos=None)
                        time.sleep(min(1.0, max(0.0, next_due - now_mono)))
                else:
                    if photos_taken >= max_photos:
                        _update_config(enabled=False, photos_taken=0, remaining_photos=0, next_shot_epoch=None)
                        session_active = False
                        photos_taken = 0
                        next_due = None
                        time.sleep(0.5)
                        continue

                    if next_due is None or now_mono >= next_due:
                        take_photo()
                        photos_taken += 1
                        remaining = max(0, max_photos - photos_taken)
                        if remaining > 0:
                            next_due = now_mono + interval_sec
                            _update_config(photos_taken=photos_taken, remaining_photos=remaining, next_shot_epoch=float(time.time() + interval_sec))
                        else:
                            _update_config(photos_taken=photos_taken, remaining_photos=0, next_shot_epoch=None, enabled=False)
                            session_active = False
                            photos_taken = 0
                            next_due = None
                    else:
                        remaining = max(0, max_photos - photos_taken)
                        _update_config(remaining_photos=remaining, next_shot_epoch=float(time.time() + max(0, next_due - now_mono)))
                        time.sleep(min(1.0, max(0.0, next_due - now_mono)))
        else:
            if session_active:
                session_active = False
                photos_taken = 0
                next_due = None
                last_burst_time = 0.0
                burst_intervals_done = 0
                _update_config(photos_taken=0, remaining_photos=0, next_shot_epoch=None)
            time.sleep(0.5)

def start_auto_capture():
    global _worker
    with _worker_lock:
        if _worker is not None and _worker.is_alive():
            return
        _worker = threading.Thread(target=loop, daemon=True)
        _worker.start()

