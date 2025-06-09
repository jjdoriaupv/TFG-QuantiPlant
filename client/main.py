from auto_capture import start_auto_capture
import time

def main():
    print("=== CLIENTE INICIADO ===")
    start_auto_capture()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Finalizado por el usuario.")

if __name__ == '__main__':
    main()


