from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import requests
import json

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
RASPBERRIES_FILE = 'raspberries.json'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def get_raspberry_list():
    with open(RASPBERRIES_FILE) as f:
        return json.load(f)

@app.route('/')
def index():
    raspberries = get_raspberry_list()
    return render_template('index.html', raspberries=raspberries)

@app.route('/galeria')
def galeria():
    files = sorted(os.listdir(UPLOAD_FOLDER), reverse=True)
    return render_template('galeria.html', images=files, server_url=request.host_url.rstrip('/'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/eliminar/<filename>', methods=['POST'])
def eliminar(filename):
    try:
        os.remove(os.path.join(UPLOAD_FOLDER, filename))
        return redirect(url_for('galeria'))
    except Exception as e:
        return f"No se pudo eliminar la imagen: {e}", 500


@app.route('/config/<device_id>', methods=['GET', 'POST'])
def config(device_id):
    raspberries = get_raspberry_list()
    raspberry = next((r for r in raspberries if r['id'] == device_id), None)

    if not raspberry:
        return "Raspberry no encontrada", 404

    if request.method == 'POST':
        interval = int(request.form['interval'])
        enabled = 'enabled' in request.form

        try:
            res = requests.post(f"http://{raspberry['host']}:6000/config", json={
                "enabled": enabled,
                "interval": interval
            })
        except Exception as e:
            return f"Error configurando {device_id}: {e}", 500

        return redirect(url_for('index'))

    # GET: mostrar configuración actual
    try:
        res = requests.get(f"http://{raspberry['host']}:6000/config")
        config_data = res.json()
    except Exception:
        config_data = {"enabled": False, "interval": 10}

    return render_template('config.html', config=config_data, device_id=device_id)

@app.route('/foto/<device_id>', methods=['POST'])
def foto(device_id):
    raspberries = get_raspberry_list()
    raspberry = next((r for r in raspberries if r['id'] == device_id), None)

    if not raspberry:
        return "Raspberry no encontrada", 404

    try:
        res = requests.post(f"http://{raspberry['host']}:6000/foto")
        if res.status_code == 200:
            return redirect(url_for('index'))
    except Exception as e:
        return f"Error al tomar foto: {e}", 500

    return "Error desconocido", 500

@app.route('/foto', methods=['POST'])
def foto():
    print(">>> [API] Recibida orden para tomar foto.")
    try:
        threading.Thread(target=take_photo, daemon=True).start()
        return "Captura iniciada", 200
    except Exception as e:
        print(f"[ERROR] al ejecutar take_photo: {e}")
        return f"Error al capturar: {e}", 500


@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('image')
    rpi_id = request.form.get('rpi_id', 'unknown')

    if file:
        filename = file.filename
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        print(f"[UPLOAD] Imagen guardada: {filepath}")
        return "OK", 200
    return "No file received", 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)



