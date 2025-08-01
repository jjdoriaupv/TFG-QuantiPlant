import subprocess
from datetime import datetime
import time
import os
import threading
from core.config_state import get_config

camera_lock = threading.Lock()

def take_photo(path=None):
    with camera_lock:
        config = get_config()

        if path is None:
            folder = config.get('save_folder', 'default')
            path = os.path.join("web/uploads", folder)

        os.makedirs(path, exist_ok=True)

        exposure = config.get('exposure', 1000)
        led_auto = config.get('led_auto', False)
        led_enabled = config.get('led_enabled', True)
        shutter_time = str(exposure)

        if led_auto:
            try:
                subprocess.run(
                    ['/home/jeremy/TFG-QuantiPlant/scripts/toggle_usb.sh', '1-1', 'bind'],
                    check=True
                )
                time.sleep(1)
            except:
                pass

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        final_filename = f"{timestamp}.png"
        final_filepath = os.path.join(path, final_filename)

        try:
            proc = subprocess.Popen(
                ["rpicam-still", "--shutter", shutter_time, "--gain", "1", "--awbgains", "1,1",
                 "--nopreview", "--encoding", "png", "-o", final_filepath]
            )
            proc.wait()
            return final_filename
        except:
            return None
        finally:
            if led_auto:
                try:
                    time.sleep(1)
                    subprocess.run(
                        ['/home/jeremy/TFG-QuantiPlant/scripts/toggle_usb.sh', '1-1', 'unbind'],
                        check=True
                    )
                except:
                    pass



