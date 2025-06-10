from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import requests
import json
import shutil
import subprocess

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
RASPBERRIES_FILE = 'raspberries.json'

# Asegurarnos de que la carpeta uploads existe
def ensure_upload_folder():
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

ensure_upload_folder()

# Lectura de raspberries y carpetas
def get_raspberry_list():
    with open(RASPBERRIES_FILE) as f:
        return json.load(f)

def get_folders():
    return sorted(
        d for d in os.listdir(UPLOAD_FOLDER)
        if os.path.isdir(os.path.join(UPLOAD_FOLDER, d))
    )

# ─── PÁGINA PRINCIPAL ─────────────────────────────────────────────────────────
@app.route('/')
def index():
    raspberries = get_raspberry_list()
    folders = get_folders()
    return render_template('index.html', raspberries=raspberries, folders=folders)

# ─── CREAR CARPETA ────────────────────────────────────────────────────────────
@app.route('/crear_carpeta', methods=['POST'])
def crear_carpeta():
    nombre = request.form.get('carpeta')
    if nombre:
        os.makedirs(os.path.join(UPLOAD_FOLDER, nombre), exist_ok=True)
    return redirect(url_for('galeria_root'))

# ─── ELIMINAR CARPETA ──────────────────────────────────────────────────────────
@app.route('/eliminar_carpeta', methods=['POST'])
def eliminar_carpeta():
    carpeta = request.form.get('carpeta')
    if not carpeta:
        return "Falta nombre de carpeta", 400
    path = os.path.join(UPLOAD_FOLDER, carpeta)
    if not os.path.isdir(path):
        return "Carpeta no encontrada", 404
    try:
        shutil.rmtree(path)
    except Exception as e:
        return f"Error eliminando carpeta: {e}", 500
    return redirect(url_for('galeria_root'))

# ─── GESTOR DE CARPETAS / GALERÍA ─────────────────────────────────────────────
@app.route('/galeria')
def galeria_root():
    folders = get_folders()
    return render_template('galeria.html', current_path=None, folders=folders, images=[])

@app.route('/galeria/<path:path>')
def galeria(path):
    full_path = os.path.join(UPLOAD_FOLDER, path)
    if not os.path.exists(full_path):
        return "Carpeta no encontrada", 404
    folders = get_folders()
    images = sorted(
        f for f in os.listdir(full_path)
        if os.path.isfile(os.path.join(full_path, f))
    )
    return render_template('galeria.html', current_path=path, folders=folders, images=images)

# ─── SERVIR IMÁGENES ──────────────────────────────────────────────────────────
@app.route('/uploads/<path:path>/<filename>')
def uploaded_file(path, filename):
    return send_from_directory(os.path.join(UPLOAD_FOLDER, path), filename)

# ─── ELIMINAR IMAGEN ──────────────────────────────────────────────────────────
@app.route('/eliminar/<path:path>/<filename>', methods=['POST'])
def eliminar(path, filename):
    try:
        os.remove(os.path.join(UPLOAD_FOLDER, path, filename))
        return redirect(url_for('galeria', path=path))
    except Exception as e:
        return f"No se pudo eliminar la imagen: {e}", 500

# ─── MOVER IMAGEN ─────────────────────────────────────────────────────────────
@app.route('/mover', methods=['POST'])
def mover_imagen():
    origen = request.form.get('origen')
    archivo = request.form.get('archivo')
    destino = request.form.get('destino')
    if not all([origen, archivo, destino]):
        return "Datos incompletos", 400
    origen_path = os.path.join(UPLOAD_FOLDER, origen, archivo)
    destino_dir = os.path.join(UPLOAD_FOLDER, destino)
    destino_path = os.path.join(destino_dir, archivo)
    if os.path.exists(origen_path) and os.path.exists(destino_dir):
        shutil.move(origen_path, destino_path)
    return redirect(url_for('galeria', path=origen))

# ─── SUBIDA DE IMÁGENES DESDE RASPBERRY ───────────────────────────────────────
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('image')
    rpi_id = request.form.get('rpi_id', 'unknown')
    carpeta = request.form.get('carpeta', rpi_id)
    path = os.path.join(UPLOAD_FOLDER, carpeta)
    os.makedirs(path, exist_ok=True)
    if file:
        filename = file.filename
        file.save(os.path.join(path, filename))
        return "OK", 200
    return "No file received", 400

# ─── TOMAR FOTO REMOTA ────────────────────────────────────────────────────────
@app.route('/foto/<device_id>', methods=['POST'])
def foto(device_id):
    carpeta = request.form.get('carpeta', device_id)
    raspberries = get_raspberry_list()
    raspberry = next((r for r in raspberries if r['id'] == device_id), None)
    if not raspberry:
        return "Raspberry no encontrada", 404
    try:
        res = requests.post(
            f"http://{raspberry['host']}:6000/foto",
            json={"carpeta": carpeta}
        )
        if res.status_code == 200:
            return redirect(url_for('galeria', path=carpeta))
    except Exception as e:
        return f"Error al tomar foto: {e}", 500
    return "Error desconocido", 500

# ─── CONFIGURACIÓN REMOTA ────────────────────────────────────────────────────
@app.route('/config/<device_id>', methods=['GET', 'POST'])
def config(device_id):
    raspberries = get_raspberry_list()
    raspberry = next((r for r in raspberries if r['id'] == device_id), None)
    if not raspberry:
        return "Raspberry no encontrada", 404
    if request.method == 'POST':
        interval = int(request.form['interval'])
        enabled = 'enabled' in request.form
        exposure = min(int(request.form.get('exposure', 1000)), 60000)
        try:
            requests.post(
                f"http://{raspberry['host']}:6000/config",
                json={"enabled": enabled,
                      "interval": interval,
                      "exposure": exposure}
            )
        except Exception as e:
            return f"Error configurando {device_id}: {e}", 500
        return redirect(url_for('index'))
    try:
        res = requests.get(f"http://{raspberry['host']}:6000/config")
        config_data = res.json()
    except Exception:
        config_data = {"enabled": False, "interval": 10, "exposure": 1000}
    return render_template('config.html', config=config_data, device_id=device_id)

@app.route('/toggle_usb/<device_id>', methods=['POST'])
def toggle_usb(device_id):
    action = request.form.get('action')
    if action not in ['on', 'off']:
        return "Acción no válida", 400

    cmd = ['/home/jeremy/TFG-QuantiPlant/client/toggle_usb.sh', '1-1', 'unbind' if action == 'off' else 'bind']

    try:
        subprocess.run(cmd, check=True)
        return redirect(url_for('config', device_id=device_id))
    except subprocess.CalledProcessError as e:
        return f"Error al ejecutar comando: {e}", 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)