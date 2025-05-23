from flask import Flask, render_template
from camera import take_photo
from led_display import send_text_to_led

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/foto')
def foto():
    filename = take_photo()
    if filename:
        return render_template('index.html', photo=filename)
    else:
        return render_template('index.html', error="Error al tomar la foto")

@app.route('/mostrar')
def mostrar():
    ok = send_text_to_led("Hola")
    return render_template('index.html', led="Texto enviado" if ok else "Error al enviar texto al LED")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
