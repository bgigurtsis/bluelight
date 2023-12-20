import subprocess
import re
import threading
import time
import random
from gpiozero import PWMOutputDevice
from guizero import App, Slider

# Set up the GPIO for the LED
pin = PWMOutputDevice(18)

# Default intensity when beacon is not detected (range 0 to 1)
default_intensity = 0.1  # Lower default intensity to symbolize calmness

def get_connected_devices():
    # Use 'bluetoothctl' to list connected devices
    result = subprocess.run(['bluetoothctl', 'info'], stdout=subprocess.PIPE)
    output = result.stdout.decode('utf-8')
    devices = re.findall(r'Device ([0-9A-F:]+) ', output)
    return devices

def get_rssi(device_address):
    # Use 'hcitool' to get the RSSI of a given device
    result = subprocess.run(['hcitool', 'rssi', device_address], stdout=subprocess.PIPE)
    output = result.stdout.decode('utf-8')
    rssi = re.search(r'RSSI return value: (-?\d+)', output)
    return int(rssi.group(1)) if rssi else None

def map_value(x, in_min, in_max, out_min, out_max):
    """Map a value from one range to another."""
    # Adjust RSSI value to handle positive values and 0
    x = min(x, 0)
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def flicker_intensity(intensity):
    """Apply flickering effect to the LED based on intensity."""
    if intensity > 0:
        on_time = random.uniform(0.05, max(0.1, 1 - intensity))
        off_time = random.uniform(0.05, max(0.1, 1 - intensity))
        pin.on()
        time.sleep(on_time)
        pin.off()
        time.sleep(off_time)
    else:
        pin.off()

def auto_control():
    """Automatically control LED based on Bluetooth beacon's RSSI to represent emotional intensity."""
    while True:
        devices = get_connected_devices()
        intensity = default_intensity
        if devices:
            for device in devices:
                rssi = get_rssi(device)
                if rssi is not None:
                    # Intensity increases as RSSI gets stronger (closer)
                    intensity = map_value(rssi, -100, 0, 1, 0)
                    print(f"Device {device} RSSI: {rssi}. Emotional Intensity: {intensity}")
                else:
                    print(f"Device {device} RSSI not available. Default calm state.")

        intensity = max(0, min(1, intensity))  # Constrain to 0-1
        flicker_intensity(intensity)
        time.sleep(0.1)  # Delay between flickers

def slider_changed(percent):
    """Manually control the LED intensity using the slider."""
    pin.value = int(percent) / 100

def main():
    # Start the auto control thread
    thread = threading.Thread(target=auto_control, daemon=True)
    thread.start()

    # Set up the GUI
    app = App(title='Emotional Intensity Control', width=500, height=150)
    slider = Slider(app, command=slider_changed, width='fill', height=50)
    slider.text_size = 30
    app.display()

if __name__ == "__main__":
    main()
