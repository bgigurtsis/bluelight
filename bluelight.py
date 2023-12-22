import asyncio
import threading
from gpiozero import PWMOutputDevice
from bleak import BleakScanner
import time

# Set up the GPIO for the LED
pin = PWMOutputDevice(18)

# Minimum and maximum intensities for visible light
min_intensity = 0.05
max_intensity = 1.0

# Global variables
latest_rssi = None
last_valid_rssi = None  # Store the last valid RSSI
should_continue = True

def map_value(x, in_min, in_max, out_min, out_max):
    """Map a value from one range to another."""
    x = max(min(x, in_max), in_min)
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def adjust_led_intensity(rssi_intensity):
    """Adjust LED intensity based on the mapped value."""
    visible_intensity = max(min_intensity, min(max_intensity, rssi_intensity))
    pin.value = visible_intensity

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
        await asyncio.sleep(0.5)  # Increased delay

def auto_control():
    """Automatically control LED based on Bluetooth beacon's RSSI."""
    global latest_rssi, last_valid_rssi, should_continue
    while should_continue:
        rssi_value = latest_rssi if latest_rssi is not None else last_valid_rssi
        if rssi_value is not None:
            rssi_intensity = map_value(rssi_value, -85, -40, 0, 1)
            print(f"RSSI: {rssi_value}, Intensity: {rssi_intensity:.2f}")
        else:
            rssi_intensity = 0

        adjust_led_intensity(rssi_intensity)
        time.sleep(0.1)  # Increased delay

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
