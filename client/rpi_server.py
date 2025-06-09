from flask import Flask, request, jsonify
from auto_capture import enable_capture, set_interval, get_config
from camera import take_photo
import threading

app = Flask(__name__)

@app.route('/foto', methods=['POST'])
def foto():
    print(">>> [API] Recibida orden para tomar foto.")
    try:
        threading.Thread(target=take_photo, daemon=True).start()
        print("[API] Captura iniciada correctamente.")
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
            print("[API] Configuración actualizada.")
            return "Configuración actualizada", 200
        except Exception as e:
            print(f"[ERROR] al configurar: {e}")
            return f"Error en configuración: {e}", 400
    else:  # GET
        config_data = get_config()
        print(f"[API] Config actual enviada: {config_data}")
        return jsonify(config_data)

if __name__ == '__main__':
    print("=== Servidor Flask del cliente iniciado en puerto 6000 ===")
    app.run(host='0.0.0.0', port=6000)
