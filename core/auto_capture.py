import threading
import time
from core.camera import take_photo
from core.config_state import get_config, save_config

_worker = None
_worker_lock = threading.Lock()

def _update(**kv):
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
            _update(photos_taken=0, remaining_photos=(max_photos if max_photos > 0 else None), next_shot_epoch=float(time.time()))

        if enabled:
            cfg = get_config()
            burst_mode_enabled = cfg.get('burst_mode_enabled', False)

            if burst_mode_enabled:
                max_intervals = int(cfg.get('max_intervals', 0))
                burst_count = int(cfg.get('burst_count', 0))
                interval_between_bursts = int(cfg.get('interval_between_bursts', 3600))
                burst_interval = int(cfg.get('burst_interval', 60))

                total_planned = (max_intervals * burst_count) if max_intervals > 0 else None
                now_mono = time.monotonic()

                if (max_intervals == 0 or burst_intervals_done < max_intervals) and (last_burst_time == 0.0 or now_mono - last_burst_time >= interval_between_bursts):
                    for i in range(burst_count):
                        take_photo()
                        photos_taken += 1
                        remaining = None if total_planned is None else max(0, total_planned - photos_taken)
                        if i < burst_count - 1:
                            _update(photos_taken=photos_taken, remaining_photos=remaining, next_shot_epoch=float(time.time() + burst_interval))
                            time.sleep(burst_interval)
                        else:
                            _update(photos_taken=photos_taken, remaining_photos=remaining)
                    burst_intervals_done += 1
                    last_burst_time = time.monotonic()
                    if max_intervals > 0 and burst_intervals_done >= max_intervals:
                        _update(enabled=False, remaining_photos=0, next_shot_epoch=None)
                        session_active = False
                        photos_taken = 0
                        next_due = None
                    else:
                        eta = float(time.time() + interval_between_bursts)
                        _update(next_shot_epoch=eta)
                else:
                    wait = 0 if last_burst_time == 0.0 else max(0, (last_burst_time + interval_between_bursts) - now_mono)
                    remaining = None if total_planned is None else max(0, total_planned - photos_taken)
                    _update(remaining_photos=remaining, next_shot_epoch=float(time.time() + wait))
                    time.sleep(0.5)
            else:
                max_photos = int(cfg.get('max_photos', 0))
                interval_sec = max(1, int(cfg.get('interval', 10)))
                now_mono = time.monotonic()

                if max_photos == 0:
                    if next_due is None or now_mono >= next_due:
                        take_photo()
                        photos_taken += 1
                        next_due = now_mono + interval_sec
                        _update(photos_taken=photos_taken, remaining_photos=None, next_shot_epoch=float(time.time() + interval_sec))
                    else:
                        _update(remaining_photos=None, next_shot_epoch=float(time.time() + max(0, next_due - now_mono)))
                        time.sleep(min(1.0, max(0.0, next_due - now_mono)))
                else:
                    if photos_taken >= max_photos:
                        _update(enabled=False, photos_taken=0, remaining_photos=0, next_shot_epoch=None)
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
                            _update(photos_taken=photos_taken, remaining_photos=remaining, next_shot_epoch=float(time.time() + interval_sec))
                        else:
                            _update(photos_taken=photos_taken, remaining_photos=0, next_shot_epoch=None, enabled=False)
                            session_active = False
                            photos_taken = 0
                            next_due = None
                    else:
                        remaining = max(0, max_photos - photos_taken)
                        _update(remaining_photos=remaining, next_shot_epoch=float(time.time() + max(0, next_due - now_mono)))
                        time.sleep(min(1.0, max(0.0, next_due - now_mono)))
        else:
            if session_active:
                session_active = False
                photos_taken = 0
                next_due = None
                last_burst_time = 0.0
                burst_intervals_done = 0
                _update(photos_taken=0, remaining_photos=0, next_shot_epoch=None)
            time.sleep(0.5)

def start_auto_capture():
    global _worker
    with _worker_lock:
        if _worker is not None and _worker.is_alive():
            return
        _worker = threading.Thread(target=loop, daemon=True)
        _worker.start()
