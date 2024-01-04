import asyncio
import threading
from gpiozero import PWMOutputDevice
from bleak import BleakScanner
import time
import random

# Set up the GPIO for the LEDs
led_pins = [15, 18, 19]
leds = [PWMOutputDevice(pin) for pin in led_pins]

# Minimum and maximum intensities for visible light
min_intensity = 0.05
max_intensity = 1.0

# Range for random intensity fluctuation
intensity_fluctuation_range = 0.1

# Global variables
latest_rssi = None
last_valid_rssi = None  # Store the last valid RSSI
should_continue = True

def map_value(x, in_min, in_max, out_min, out_max):
    """Map a value from one range to another."""
    return max(min(max(min(x, in_max), in_min), out_max), out_min)

def adjust_led_intensity(rssi_intensity):
    """Adjust LED intensity for all LEDs based on the mapped value with random fluctuation."""
    base_intensity = map_value(rssi_intensity, min_intensity, max_intensity, 0, 1)
    for led in leds:
        # Add random fluctuation to the base intensity
        fluctuation = random.uniform(-intensity_fluctuation_range, intensity_fluctuation_range)
        visible_intensity = max(min_intensity, min(max_intensity, base_intensity + fluctuation))
        led.value = visible_intensity

async def rssi_scanning():
    """Asynchronous method to continuously scan for BLE devices and update RSSI."""
    global latest_rssi, last_valid_rssi, should_continue
    target_device_address = "C9:FA:4B:21:11:26"

    while should_continue:
        devices = await BleakScanner.discover(timeout=2.0)
        for device in devices:
            if device.address == target_device_address:
                latest_rssi = device.rssi
                last_valid_rssi = latest_rssi  # Update the last valid RSSI
                break
        await asyncio.sleep(0.5)

def auto_control():
    """Automatically control LEDs based on Bluetooth beacon's RSSI."""
    global latest_rssi, last_valid_rssi, should_continue
    while should_continue:
        rssi_value = latest_rssi if latest_rssi is not None else last_valid_rssi
        if rssi_value is not None:
            rssi_intensity = map_value(rssi_value, -85, -48, 0, 1)
            print(f"RSSI: {rssi_value}, Intensity: {rssi_intensity:.2f}")
            adjust_led_intensity(rssi_intensity)
        else:
            adjust_led_intensity(0)
        time.sleep(0.1)  # Adjust for desired responsiveness

def start_async_loop(loop):
    """Starts the asynchronous event loop."""
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
