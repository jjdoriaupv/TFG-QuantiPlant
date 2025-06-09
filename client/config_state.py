config = {
    'enabled': False,
    'interval': 10,
    'exposure': 1000
}

def get_config():
    return config

def enable_capture(enabled):
    config['enabled'] = enabled

def set_interval(interval):
    config['interval'] = interval

def set_exposure(exposure):
    if exposure > 60000:
        exposure = 60000
    config['exposure'] = exposure

