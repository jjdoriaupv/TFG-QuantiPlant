import subprocess
from datetime import datetime
import os
import requests
import tempfile

SERVER_URL = "http://192.168.1.53:5001"

def take_photo():
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=True) as tmpfile:
        try:
            subprocess.run(["libcamera-jpeg", "-o", tmpfile.name], check=True)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            remote_filename = f"photo_{timestamp}.jpg"

            with open(tmpfile.name, 'rb') as f:
                files = {'image': (remote_filename, f, 'image/jpeg')}
                response = requests.post(f"{SERVER_URL}/upload", files=files)

            if response.status_code == 200:
                print(f"[UPLOAD] Foto enviada correctamente: {remote_filename}")
                return f"{SERVER_URL}/uploads/{remote_filename}"
            else:
                print(f"[UPLOAD] Fallo al subir: {response.status_code} {response.text}")
                return None

        except Exception as e:
            print(f"[ERROR] No se pudo capturar o subir la imagen: {e}")
            return None


