import subprocess
from datetime import datetime
import requests
import tempfile
import time
from config import SERVER_URL
from config_state import get_config

def take_photo(rpi_id="rpi-1"):
    print(f"[TAKE] Intentando capturar imagen para carpeta: {rpi_id}")

    config = get_config()
    exposure = config.get('exposure', 1000)
    led_auto = config.get('led_auto', False)
    shutter_time = str(exposure * 1000)

    if led_auto:
        try:
            subprocess.run(['/home/jeremy/TFG-QuantiPlant/client/toggle_usb.sh', '1-1', 'bind'], check=True)
            print("[LED] Encendido antes de captura")
            time.sleep(1)
        except Exception as e:
            print(f"[LED] Error al encender LED automáticamente: {e}")

    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=True) as tmpfile:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{rpi_id}_{timestamp}.jpg"

        try:
            subprocess.run(
                ["libcamera-jpeg", "--shutter", shutter_time, "-o", tmpfile.name],
                check=True
            )
            print("[TAKE] Imagen capturada, enviando al servidor...")

            with open(tmpfile.name, 'rb') as f:
                files = {'image': (filename, f, 'image/jpeg')}
                data = {'rpi_id': rpi_id, 'carpeta': rpi_id}
                response = requests.post(f"{SERVER_URL}/upload", files=files, data=data)

            print(f"[UPLOAD] Status: {response.status_code}, Body: {response.text}")
            if response.status_code == 200:
                print(f"[UPLOAD] Foto enviada correctamente: {filename}")
            else:
                print(f"[UPLOAD] Fallo al subir: {response.status_code} {response.text}")

        except Exception as e:
            print(f"[ERROR] No se pudo capturar o subir la imagen: {e}")

    if led_auto:
        try:
            time.sleep(1)
            subprocess.run(['/home/jeremy/TFG-QuantiPlant/client/toggle_usb.sh', '1-1', 'unbind'], check=True)
            print("[LED] Apagado después de captura")
        except Exception as e:
            print(f"[LED] Error al apagar LED automáticamente: {e}")
