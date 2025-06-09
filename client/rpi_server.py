from flask import Flask, request, jsonify
from auto_capture import enable_capture, set_interval, get_config
from camera import take_photo
import threading

app = Flask(__name__)

@app.route('/foto', methods=['POST'])
def foto():
    try:
        threading.Thread(target=take_photo, daemon=True).start()
        return "Captura iniciada", 200
    except Exception as e:
        return f"Error al capturar: {e}", 500

@app.route('/config', methods=['GET', 'POST'])
def config():
    if request.method == 'POST':
        data = request.get_json()
        enable_capture(data.get("enabled", False))
        set_interval(data.get("interval", 10))
        return "Configuración actualizada", 200
    else:  # GET
        return jsonify(get_config())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000)
