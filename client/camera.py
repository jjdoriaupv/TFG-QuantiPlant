import subprocess
from datetime import datetime
import requests
import tempfile
from config import SERVER_URL

def take_photo(rpi_id="rpi-1"):
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=True) as tmpfile:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{rpi_id}_{timestamp}.jpg"

        try:
            subprocess.run(["libcamera-jpeg", "-o", tmpfile.name], check=True)
            with open(tmpfile.name, 'rb') as f:
                files = {'image': (filename, f, 'image/jpeg')}
                data = {'rpi_id': rpi_id}
                response = requests.post(f"{SERVER_URL}/upload", files=files, data=data)
            if response.status_code == 200:
                print(f"[UPLOAD] Foto enviada correctamente: {filename}")
            else:
                print(f"[UPLOAD] Fallo al subir: {response.status_code} {response.text}")
        except Exception as e:
            print(f"[ERROR] No se pudo capturar o subir la imagen: {e}")