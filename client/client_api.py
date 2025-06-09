# client_api.py

from flask import Flask, request, jsonify
from camera import take_photo
from auto_capture import start_auto_capture, enable_capture, set_interval, get_config
import threading

app = Flask(__name__)

@app.route('/foto', methods=['POST'])
def foto():
    filename = take_photo()
    if filename:
        return jsonify({"status": "ok", "filename": filename}), 200
    else:
        return jsonify({"status": "error", "message": "No se pudo tomar la foto"}), 500

@app.route('/config', methods=['POST'])
def config():
    data = request.get_json()
    if data is None:
        return jsonify({"status": "error", "message": "JSON no válido"}), 400

    enabled = data.get('enabled')
    interval = data.get('interval')

    if enabled is not None:
        enable_capture(bool(enabled))
    if interval is not None:
        set_interval(int(interval))

    return jsonify({"status": "ok", "message": "Configuración actualizada"}), 200

@app.route('/config', methods=['GET'])
def get_config_route():
    return jsonify(get_config()), 200

def run_flask():
    app.run(host='0.0.0.0', port=6000)

if __name__ == '__main__':
    print("[CLIENT] Iniciando API Flask en /foto y /config...")
    start_auto_capture()
    run_flask()

