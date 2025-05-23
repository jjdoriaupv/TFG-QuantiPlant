import subprocess
from datetime import datetime
import os
import requests

def take_photo():
    if not os.path.exists("static"):
        os.makedirs("static")

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    local_path = f"static/photo_{timestamp}.jpg"

    try:
        subprocess.run(["libcamera-jpeg", "-o", local_path], check=True)

        with open(local_path, 'rb') as f:
            files = {'image': (f"photo_{timestamp}.jpg", f, 'image/jpeg')}
            response = requests.post("http://192.168.1.53:5001/upload", files=files)
            if response.status_code == 200:
                print(f"[UPLOAD] Foto enviada correctamente")
            else:
                print(f"[UPLOAD] Error al subir: {response.text}")

        return local_path
    except subprocess.CalledProcessError:
        return None


