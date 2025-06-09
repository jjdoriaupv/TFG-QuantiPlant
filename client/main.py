from auto_capture import start_auto_capture
from config_state import enable_capture, set_interval, set_exposure, get_config
from flask import Flask, request, jsonify
from camera import take_photo
import threading
import time

app = Flask(__name__)

# === API SERVER ===

@app.route('/foto', methods=['POST'])
def foto():
    print(">>> [API] Recibida orden para tomar foto.")
    try:
        threading.Thread(target=take_photo, daemon=True).start()
        return "Captura iniciada", 200
    except Exception as e:
        print(f"[ERROR] al ejecutar take_photo: {e}")
        return f"Error al capturar: {e}", 500

@app.route('/config', methods=['GET', 'POST'])
def config():
    if request.method == 'POST':
        data = request.get_json()
        print(f">>> [API] Configuración recibida: {data}")
        try:
            enable_capture(data.get("enabled", False))
            set_interval(int(data.get("interval", 10)))
            set_exposure(int(data.get("exposure", 1000)))
            return "Configuración actualizada", 200
        except Exception as e:
            return f"Error en configuración: {e}", 400
    else:
        return jsonify(get_config())

# === MAIN ===

def run_flask():
    print("=== Servidor Flask del cliente iniciado en puerto 6000 ===")
    app.run(host='0.0.0.0', port=6000)

def main():
    print("=== CLIENTE INICIADO ===")
    start_auto_capture()

    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Finalizado por el usuario.")

if __name__ == '__main__':
    main()



