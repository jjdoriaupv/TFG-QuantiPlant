from flask import Flask, request, send_from_directory, send_file, jsonify, render_template
from datetime import datetime
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    folders = sorted(os.listdir(UPLOAD_FOLDER))
    all_images = []
    for folder in folders:
        folder_path = os.path.join(UPLOAD_FOLDER, folder)
        if os.path.isdir(folder_path):
            for file in os.listdir(folder_path):
                all_images.append((folder, file))
    return render_template("index.html", images=all_images)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('image')
    rpi_id = request.form.get('rpi_id', 'unknown')
    if not file:
        return 'No image received', 400

    folder = os.path.join(UPLOAD_FOLDER, rpi_id)
    os.makedirs(folder, exist_ok=True)
    filename = file.filename
    file.save(os.path.join(folder, filename))
    print(f"[UPLOAD] {filename} recibido de {rpi_id}")
    return 'OK', 200

@app.route('/uploads/<rpi_id>/<filename>')
def get_image(rpi_id, filename):
    return send_from_directory(os.path.join(UPLOAD_FOLDER, rpi_id), filename)

@app.route('/download/<rpi_id>/<filename>')
def download_image(rpi_id, filename):
    path = os.path.join(UPLOAD_FOLDER, rpi_id, filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return 'Not found', 404

@app.route('/delete/<rpi_id>/<filename>', methods=['POST'])
def delete_image(rpi_id, filename):
    path = os.path.join(UPLOAD_FOLDER, rpi_id, filename)
    if os.path.exists(path):
        os.remove(path)
        return 'Deleted', 200
    return 'Not found', 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)