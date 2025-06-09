# client_api.py
from flask import Flask, render_template, request, redirect, url_for
from camera import take_photo
from led_display import send_text_to_led
from auto_capture import start_auto_capture, enable_capture, set_interval, get_config
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/foto', methods=['POST'])
def foto():
    take_photo()
    return '', 204  # No content, no redirect, no page reload

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

if __name__ == '__main__':
    start_auto_capture()
    app.run(host='0.0.0.0', port=5000)

