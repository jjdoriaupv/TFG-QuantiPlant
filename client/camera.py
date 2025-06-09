import subprocess
from datetime import datetime
import requests
import tempfile
from config import SERVER_URL
from config_state import get_config

def take_photo(rpi_id="rpi-1"):
    print("[TAKE] Intentando capturar imagen...")

    config = get_config()
    exposure = config.get('exposure', 1000)  # milisegundos por defecto
    shutter_time = str(exposure * 1000)  # convertir a microsegundos

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
                data = {'rpi_id': rpi_id}
                response = requests.post(f"{SERVER_URL}/upload", files=files, data=data)

            print(f"[UPLOAD] Status: {response.status_code}, Body: {response.text}")

            if response.status_code == 200:
                print(f"[UPLOAD] Foto enviada correctamente: {filename}")
            else:
                print(f"[UPLOAD] Fallo al subir: {response.status_code} {response.text}")
        except Exception as e:
            print(f"[ERROR] No se pudo capturar o subir la imagen: {e}")
