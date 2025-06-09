from flask import Flask, render_template, request, redirect, url_for, jsonify
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
    return render_template('galeria.html', images=files)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return redirect(f"/uploads/{filename}")

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
