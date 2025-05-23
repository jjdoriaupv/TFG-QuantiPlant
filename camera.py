import subprocess
from datetime import datetime
import os

def take_photo():
    if not os.path.exists("static"):
        os.makedirs("static")

    filename = f"static/photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    
    try:
        subprocess.run(["libcamera-jpeg", "-o", filename], check=True)
        return filename
    except subprocess.CalledProcessError:
        return None

