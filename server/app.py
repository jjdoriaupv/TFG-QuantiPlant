from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import requests
import json
import shutil

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
RASPBERRIES_FILE = 'raspberries.json'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def get_raspberry_list():
    with open(RASPBERRIES_FILE) as f:
        return json.load(f)

def get_folders():
    return sorted([d for d in os.listdir(UPLOAD_FOLDER) if os.path.isdir(os.path.join(UPLOAD_FOLDER, d))])

@app.route('/')
def index():
    raspberries = get_raspberry_list()
    folders = get_folders()
    return render_template('index.html', raspberries=raspberries, folders=folders)

@app.route('/crear_carpeta', methods=['POST'])
def crear_carpeta():
    nombre = request.form.get('carpeta')
    if nombre:
        os.makedirs(os.path.join(UPLOAD_FOLDER, nombre), exist_ok=True)
    return redirect(url_for('index'))

@app.route('/galeria')
def lista_carpetas():
    carpetas = get_folders()
    return render_template('galeria_carpetas.html', carpetas=carpetas)

@app.route('/galeria/<carpeta>')
def galeria(carpeta):
    path = os.path.join(UPLOAD_FOLDER, carpeta)
    if not os.path.exists(path):
        return "Carpeta no encontrada", 404
    images = sorted(os.listdir(path), reverse=True)
    return render_template('galeria.html', images=images, carpeta=carpeta, server_url=request.host_url.rstrip('/'))

@app.route('/uploads/<carpeta>/<filename>')
def uploaded_file(carpeta, filename):
    return send_from_directory(os.path.join(UPLOAD_FOLDER, carpeta), filename)

@app.route('/eliminar/<carpeta>/<filename>', methods=['POST'])
def eliminar(carpeta, filename):
    try:
        os.remove(os.path.join(UPLOAD_FOLDER, carpeta, filename))
        return redirect(url_for('galeria', carpeta=carpeta))
    except Exception as e:
        return f"No se pudo eliminar la imagen: {e}", 500

@app.route('/mover/<carpeta>/<filename>', methods=['POST'])
def mover(carpeta, filename):
    destino = request.form.get('destino')
    origen_path = os.path.join(UPLOAD_FOLDER, carpeta, filename)
    destino_path = os.path.join(UPLOAD_FOLDER, destino, filename)
    if os.path.exists(origen_path) and os.path.exists(os.path.join(UPLOAD_FOLDER, destino)):
        shutil.move(origen_path, destino_path)
    return redirect(url_for('galeria', carpeta=carpeta))

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('image')
    rpi_id = request.form.get('rpi_id', 'unknown')
    carpeta = request.form.get('carpeta', rpi_id)
    
    path = os.path.join(UPLOAD_FOLDER, carpeta)
    os.makedirs(path, exist_ok=True)

    if file:
        filename = file.filename
        filepath = os.path.join(path, filename)
        file.save(filepath)
        print(f"[UPLOAD] Imagen guardada: {filepath}")
        return "OK", 200
    return "No file received", 400

@app.route('/foto/<device_id>', methods=['POST'])
def foto(device_id):
    carpeta = request.form.get('carpeta', device_id)
    raspberries = get_raspberry_list()
    raspberry = next((r for r in raspberries if r['id'] == device_id), None)

    if not raspberry:
        return "Raspberry no encontrada", 404

    try:
        res = requests.post(f"http://{raspberry['host']}:6000/foto", json={"carpeta": carpeta})
        if res.status_code == 200:
            return redirect(url_for('index'))
    except Exception as e:
        return f"Error al tomar foto: {e}", 500

    return "Error desconocido", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)