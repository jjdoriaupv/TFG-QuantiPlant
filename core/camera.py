import subprocess
from datetime import datetime
import time
import os
from core.config_state import get_config

def take_photo(path=None):
    config = get_config()
    if path is None:
        folder = config.get('save_folder', 'default')
        path = os.path.join("web/uploads", folder)

    print(f"[TAKE] Capturando imagen en: {path}")
    os.makedirs(path, exist_ok=True)

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
    raw_filename = f"{timestamp}_raw.jpg"
    final_filename = f"{timestamp}.jpg"

    raw_filepath = os.path.join(path, raw_filename)
    final_filepath = os.path.join(path, final_filename)

    try:
        subprocess.run(
            ["libcamera-jpeg", "--shutter", shutter_time, "--nopreview", "-o", raw_filepath],
            check=True
        )

        # Voltear horizontalmente usando ImageMagick (convert)
        subprocess.run(
            ["convert", raw_filepath, "-flop", final_filepath],
            check=True
        )

        os.remove(raw_filepath)

        print(f"[TAKE] Imagen final guardada: {final_filepath}")
        return final_filename

    except Exception as e:
        print(f"[ERROR] No se pudo capturar o procesar la imagen: {e}")
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

