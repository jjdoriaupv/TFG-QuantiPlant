import serial

def send_text_to_led(text):
    try:
        ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
        ser.write((text + '\n').encode('utf-8'))
        ser.close()
        return True
    except Exception as e:
        print("Error al enviar texto al LED:", e)
        return False
