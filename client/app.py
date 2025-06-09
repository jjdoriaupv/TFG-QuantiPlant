from camera import take_photo
from auto_capture import start_auto_capture, enable_capture, set_interval, get_config
import time

def main():
    print("[CLIENT] Iniciando Raspberry...")
    
    # Puedes configurar esto según tu necesidad
    enable_capture(True)
    set_interval(10)

    start_auto_capture()

    try:
        while True:
            time.sleep(1)  # Mantiene la app corriendo
    except KeyboardInterrupt:
        print("\n[CLIENT] Finalizado por el usuario")

if __name__ == '__main__':
    main()
