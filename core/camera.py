import subprocess
from datetime import datetime
import time
import os
from core.config_state import get_config

def take_photo(path="web/uploads/default"):
    print(f"[TAKE] Capturando imagen en: {path}")
    os.makedirs(path, exist_ok=True)

    config = get_config()
    exposure = config.get('exposure', 1000)
    led_auto = config.get('led_auto', False)
    shutter_time = str(exposure * 1000)

    if led_auto:
        try:
            subprocess.run(
                ['/home/jeremy/TFG-QuantiPlant/scripts/toggle_usb.sh', '1-1', 'bind'],
                check=True
            )
            print("[LED] Encendido automático")
            time.sleep(1)
        except Exception as e:
            print(f"[LED] Error al encender: {e}")

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{timestamp}.jpg"
    filepath = os.path.join(path, filename)

    try:
        subprocess.run(
            ["libcamera-jpeg", "--shutter", shutter_time, "--nopreview", "-o", filepath],
            check=True
        )
        print(f"[TAKE] Imagen guardada: {filepath}")
        return filename
    except Exception as e:
        print(f"[ERROR] No se pudo capturar imagen: {e}")
        return None
    finally:
        if led_auto:
            try:
                time.sleep(1)
                subprocess.run(
                    ['/home/jeremy/TFG-QuantiPlant/scripts/toggle_usb.sh', '1-1', 'unbind'],
                    check=True
                )
                print("[LED] Apagado automático")
            except Exception as e:
                print(f"[LED] Error al apagar: {e}")
