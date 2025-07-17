import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, send_file
import shutil
from core.camera import take_photo
from core.config_state import get_config, set_config
from core.auto_capture import start_auto_capture
import subprocess
import zipfile
import io

app = Flask(__name__)
UPLOAD_FOLDER = 'web/uploads'

start_auto_capture()

def ensure_upload_folder():
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

ensure_upload_folder()

def get_folders():
    return sorted(
        d for d in os.listdir(UPLOAD_FOLDER)
        if os.path.isdir(os.path.join(UPLOAD_FOLDER, d))
    )

def is_usb_bound():
    path = "/sys/bus/usb/drivers/usb/1-1"
    return os.path.exists(path)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/crear_carpeta', methods=['POST'])
def crear_carpeta():
    nombre = request.form.get('carpeta')
    if nombre:
        os.makedirs(os.path.join(UPLOAD_FOLDER, nombre), exist_ok=True)
    return redirect(url_for('galeria_root'))

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

@app.route('/uploads/<path:path>/<filename>')
def uploaded_file(path, filename):
    return send_from_directory(os.path.join(UPLOAD_FOLDER, path), filename)

@app.route('/eliminar/<path:path>/<filename>', methods=['POST'])
def eliminar(path, filename):
    try:
        os.remove(os.path.join(UPLOAD_FOLDER, path, filename))
        return redirect(url_for('galeria', path=path))
    except Exception as e:
        return f"No se pudo eliminar la imagen: {e}", 500

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

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('image')
    carpeta = request.form.get('carpeta', 'default')
    path = os.path.join(UPLOAD_FOLDER, carpeta)
    os.makedirs(path, exist_ok=True)
    if file:
        filename = file.filename
        file.save(os.path.join(path, filename))
        return "OK", 200
    return "No file received", 400

@app.route('/foto', methods=['POST'])
def foto():
    carpeta = request.form.get('carpeta', 'default')
    path = os.path.join(UPLOAD_FOLDER, carpeta)
    os.makedirs(path, exist_ok=True)
    try:
        take_photo(path)
        return redirect(url_for('galeria', path=carpeta))
    except Exception as e:
        return f"Error al tomar foto: {e}", 500

@app.route('/config', methods=['GET', 'POST'])
def config():
    if request.method == 'POST':
        interval = int(request.form['interval'])
        enabled = 'enabled' in request.form
        exposure = min(int(request.form.get('exposure', 1000)), 60000)
        led_auto = 'led_auto' in request.form
        led_enabled = 'led_enabled' in request.form  # <- NUEVO
        max_photos = int(request.form.get('max_photos', 0))

        folder_input = request.form.get('save_folder', '').strip()
        folder_select = request.form.get('folder_select', '').strip()
        save_folder = folder_input if folder_input else (folder_select if folder_select else 'default')

        try:
            set_config({
                "enabled": enabled,
                "interval": interval,
                "exposure": exposure,
                "led_auto": led_auto,
                "led_enabled": led_enabled,  # <- NUEVO
                "max_photos": max_photos,
                "save_folder": save_folder
            })
        except Exception as e:
            return f"Error guardando configuración: {e}", 500
        return redirect(url_for('index'))



@app.route('/toggle_usb', methods=['POST'])
def toggle_usb():
    led_on = 'led' in request.form
    usb_is_bound = is_usb_bound()

    if led_on == usb_is_bound:
        return redirect(url_for('config'))

    action = 'bind' if led_on else 'unbind'
    try:
        subprocess.run(
            ['/home/jeremy/TFG-QuantiPlant/scripts/toggle_usb.sh', '1-1', action],
            check=True
        )
        return redirect(url_for('config'))
    except Exception as e:
        return f"Error al ejecutar toggle_usb: {e}", 500
    
@app.route('/descargar_carpeta/<string:folder>')
def descargar_carpeta(folder):
    carpeta_path = os.path.join(UPLOAD_FOLDER, folder)
    if not os.path.exists(carpeta_path):
        return "Carpeta no encontrada", 404

    memoria_zip = io.BytesIO()
    with zipfile.ZipFile(memoria_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(carpeta_path):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, carpeta_path)
                zipf.write(abs_path, arcname=rel_path)
    memoria_zip.seek(0)

    nombre_zip = f"{folder.replace('/', '_')}.zip"
    return send_file(memoria_zip, mimetype='application/zip', as_attachment=True, download_name=nombre_zip)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

