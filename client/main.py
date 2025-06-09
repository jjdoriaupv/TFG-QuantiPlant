from auto_capture import start_auto_capture, enable_capture, set_interval
import time

def main():
    print("=== CLIENTE INICIADO ===")
    enable_capture(True)
    set_interval(10)
    start_auto_capture()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Finalizado por el usuario.")

if __name__ == '__main__':
    main()



