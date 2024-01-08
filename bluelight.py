import asyncio
import threading
from gpiozero import PWMOutputDevice
from bleak import BleakScanner
import time
import random

# Set up the GPIO for the LEDs
led_pins = [18, 19, 15]
leds = [PWMOutputDevice(pin) for pin in led_pins]

# RSSI values for mapping
rssi_min = -75
rssi_max = -40

# Intensity values
min_intensity = 0.0
max_intensity = 1.0

# Fluctuation Intensity Settings
min_fluctuation_intensity = 0.02
max_fluctuation_intensity = 0.1

# Global variables
latest_rssi = None
last_valid_rssi = None
should_continue = True

def map_value(x, in_min, in_max, out_min, out_max):
    return max(min((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min, out_max), out_min)

def get_intensity_fluctuation(rssi_intensity):
    fluctuation_range = max_fluctuation_intensity - min_fluctuation_intensity
    scaled_fluctuation = (rssi_intensity * fluctuation_range) + min_fluctuation_intensity
    return random.uniform(0, scaled_fluctuation)

def get_flashing_delay(rssi_intensity):
    return 1.0 - rssi_intensity

def adjust_led_intensity(rssi_intensity, dampened_intensity):
    for led in leds:
        led.value = max_intensity
        time.sleep(get_flashing_delay(dampened_intensity))
        led.value = min_intensity
        time.sleep(get_flashing_delay(dampened_intensity))

async def rssi_scanning():
    global latest_rssi, last_valid_rssi, should_continue
    target_device_address = "CA:07:23:23:7C:D1"
    while should_continue:
        device = await BleakScanner.find_device_by_address(target_device_address, timeout=2.0)
        if device:
            latest_rssi = device.rssi
            last_valid_rssi = latest_rssi
        else:
            print("Device not found. Retrying...")
        await asyncio.sleep(0.1)

def auto_control():
    global latest_rssi, last_valid_rssi, should_continue
    previous_intensity = 0
    while should_continue:
        rssi_value = latest_rssi if latest_rssi is not None else last_valid_rssi
        if rssi_value is not None:
            rssi_intensity = map_value(rssi_value, rssi_min, rssi_max, min_intensity, max_intensity)
            dampened_intensity = previous_intensity * 0.7 + rssi_intensity * 0.3
            previous_intensity = dampened_intensity
            print(f"RSSI: {rssi_value}, Intensity: {rssi_intensity:.2f}")
            adjust_led_intensity(rssi_value, dampened_intensity)
        time.sleep(0.05)

def start_async_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(rssi_scanning())

def main():
    loop = asyncio.new_event_loop()
    scan_thread = threading.Thread(target=start_async_loop, args=(loop,))
    control_thread = threading.Thread(target=auto_control)
    scan_thread.start()
    control_thread.start()
    try:
        scan_thread.join()
        control_thread.join()
    except KeyboardInterrupt:
        global should_continue
        should_continue = False
        scan_thread.join()
        control_thread.join()

if __name__ == "__main__":
    main()
