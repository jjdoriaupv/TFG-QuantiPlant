import json
import os

CONFIG_FILE = 'config.json'

default_config = {
    'enabled': False,
    'interval': 10,
    'exposure': 1000,
    'led_auto': False,
    'max_photos': 0
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        save_config(default_config)
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def save_config(data):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f)

def get_config():
    return load_config()

def enable_capture(enabled):
    config = load_config()
    config['enabled'] = enabled
    save_config(config)

def set_interval(interval):
    config = load_config()
    config['interval'] = interval
    save_config(config)

def set_exposure(exposure):
    if exposure > 60000:
        exposure = 60000
    config = load_config()
    config['exposure'] = exposure
    save_config(config)

def set_led_auto(value):
    config = load_config()
    config['led_auto'] = bool(value)
    save_config(config)

def set_config(data):
    save_config(data)
