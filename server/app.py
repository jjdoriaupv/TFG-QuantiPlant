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

def get_projects():
    return [d for d in os.listdir(UPLOAD_FOLDER) if os.path.isdir(os.path.join(UPLOAD_FOLDER, d))]

@app.route('/')
def index():
    raspberries = get_raspberry_list()
    projects = get_projects()
    return render_template('index.html', raspberries=raspberries, projects=projects)

@app.route('/crear_proyecto', methods=['POST'])
def crear_proyecto():
    nombre = request.form.get('nombre')
    if nombre:
        path = os.path.join(UPLOAD_FOLDER, nombre)
        os.makedirs(path, exist_ok=True)
    return redirect(url_for('index'))

@app.route('/galeria/<proyecto>')
def galeria(proyecto):
    path = os.path.join(UPLOAD_FOLDER, proyecto)
    if not os.path.exists(path):
        return "Proyecto no encontrado", 404
    files = sorted(os.listdir(path), reverse=True)
    return render_template('galeria.html', images=files, server_url=request.host_url.rstrip('/'), proyecto=proyecto)

@app.route('/uploads/<proyecto>/<filename>')
def uploaded_file(proyecto, filename):
    return send_from_directory(os.path.join(UPLOAD_FOLDER, proyecto), filename)

@app.route('/eliminar/<proyecto>/<filename>', methods=['POST'])
def eliminar(proyecto, filename):
    try:
        os.remove(os.path.join(UPLOAD_FOLDER, proyecto, filename))
        return redirect(url_for('galeria', proyecto=proyecto))
    except Exception as e:
        return f"No se pudo eliminar la imagen: {e}", 500

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('image')
    rpi_id = request.form.get('rpi_id', 'unknown')
    proyecto = request.form.get('proyecto', 'default')

    path = os.path.join(UPLOAD_FOLDER, proyecto)
    os.makedirs(path, exist_ok=True)

    if file:
        filename = file.filename
        filepath = os.path.join(path, filename)
        file.save(filepath)
        print(f"[UPLOAD] Imagen guardada: {filepath}")
        return "OK", 200
    return "No file received", 400

@app.route('/config/<device_id>', methods=['GET', 'POST'])
def config(device_id):
    raspberries = get_raspberry_list()
    raspberry = next((r for r in raspberries if r['id'] == device_id), None)

    if not raspberry:
        return "Raspberry no encontrada", 404

    if request.method == 'POST':
        interval = int(request.form['interval'])
        enabled = 'enabled' in request.form
        exposure = int(request.form.get('exposure', 1000))
        if exposure > 60000:
            exposure = 60000

        try:
            res = requests.post(f"http://{raspberry['host']}:6000/config", json={
                "enabled": enabled,
                "interval": interval,
                "exposure": exposure
            })
        except Exception as e:
            return f"Error configurando {device_id}: {e}", 500

        return redirect(url_for('index'))

    try:
        res = requests.get(f"http://{raspberry['host']}:6000/config")
        config_data = res.json()
    except Exception:
        config_data = {"enabled": False, "interval": 10, "exposure": 1000}

    return render_template('config.html', config=config_data, device_id=device_id)

@app.route('/foto/<device_id>', methods=['POST'])
def foto(device_id):
    proyecto = request.form.get('proyecto', 'default')
    raspberries = get_raspberry_list()
    raspberry = next((r for r in raspberries if r['id'] == device_id), None)

    if not raspberry:
        return "Raspberry no encontrada", 404

    try:
        res = requests.post(f"http://{raspberry['host']}:6000/foto", json={"proyecto": proyecto})
        if res.status_code == 200:
            return redirect(url_for('index'))
    except Exception as e:
        return f"Error al tomar foto: {e}", 500

    return "Error desconocido", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
