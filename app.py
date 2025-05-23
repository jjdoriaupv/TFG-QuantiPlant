from flask import Flask, render_template, request, redirect, url_for
from camera import take_photo
from led_display import send_text_to_led
from auto_capture import start_auto_capture, enable_capture, set_interval, get_config
import requests

app = Flask(__name__)

SERVER_URL = 'http://192.168.1.53:5001' 

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/foto')
def foto():
    filename = take_photo()
    if filename:
        return render_template('index.html', photo=filename)
    else:
        return render_template('index.html', error="No se pudo tomar la foto")

@app.route('/mostrar')
def mostrar():
    ok = send_text_to_led("Hola")
    if ok:
        return render_template('index.html', led="Texto enviado al LED")
    else:
        return render_template('index.html', led="Error al enviar texto al LED")

@app.route('/config', methods=['GET', 'POST'])
def config():
    if request.method == 'POST':
        enabled = request.form.get('enabled') == 'on'
        interval = int(request.form.get('interval'))
        enable_capture(enabled)
        set_interval(interval)
        return redirect(url_for('config'))

    config = get_config()
    return render_template('config.html', config=config)

@app.route('/download/<filename>')
def download_file(filename):
    path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return 'Not Found', 404

@app.route('/galeria')
def galeria():
    try:
        res = requests.get(f'{SERVER_URL}/list')
        if res.status_code == 200:
            images = res.json()
        else:
            images = []
    except Exception as e:
        print(f"Error al obtener lista de imágenes: {e}")
        images = []

    return render_template('galeria.html', images=images, server_url=SERVER_URL)

@app.route('/eliminar/<filename>', methods=['POST'])
def eliminar(filename):
    try:
        res = requests.delete(f'{SERVER_URL}/uploads/{filename}')
        print(f"Eliminando {filename}: {res.status_code}")
    except Exception as e:
        print(f"Error al eliminar imagen: {e}")
    return redirect(url_for('galeria'))

if __name__ == '__main__':
    start_auto_capture()
    app.run(host='0.0.0.0', port=5000)


