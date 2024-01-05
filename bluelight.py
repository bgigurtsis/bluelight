import asyncio
import threading
from gpiozero import PWMOutputDevice
from bleak import BleakScanner
import time
import random

# Set up the GPIO for the LEDs
led_pins = [18, 19, 15]
leds = [PWMOutputDevice(pin) for pin in led_pins]

# Minimum and maximum RSSI values for mapping
rssi_min = -80
rssi_max = -60

# Minimum and maximum intensities for visible light
min_intensity = 0.0
max_intensity = 1.0

# Global variables
latest_rssi = None
last_valid_rssi = None  # Store the last valid RSSI
should_continue = True

def map_value(x, in_min, in_max, out_min, out_max):
    """Map a value from one range to another."""
    return max(min((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min, out_max), out_min)

def get_intensity_fluctuation(rssi_intensity):
    """Get the intensity fluctuation based on RSSI."""
    # More fluctuation when the intensity is high, less when low
    if rssi_intensity > 0.8:
        return random.uniform(0, 0.1)
    else:
        return random.uniform(0, 0.02)

def adjust_led_intensity(rssi_intensity, dampened_intensity):
    """Adjust LED intensity for all LEDs based on the mapped value with random fluctuation."""
    for i, led in enumerate(leds):
        fluctuation = get_intensity_fluctuation(dampened_intensity)
        visible_intensity = max(min_intensity, min(max_intensity, dampened_intensity + fluctuation))
        led.value = visible_intensity
        #print(f"LED {i+1}: RSSI = {rssi_intensity}, Base Intensity = {dampened_intensity:.2f}, Visible Intensity = {visible_intensity:.2f}")

async def rssi_scanning():
    """Asynchronous method to continuously scan for a specific BLE device and update RSSI."""
    global latest_rssi, last_valid_rssi, should_continue
    target_device_address = "C9:FA:4B:21:11:26"  # Replace with your beacon's MAC address

    while should_continue:
        device = await BleakScanner.find_device_by_address(target_device_address, timeout=2.0)
        if device:
            latest_rssi = device.rssi
            last_valid_rssi = latest_rssi  # Update the last valid RSSI
        else:
            print("Device not found. Retrying...")

        await asyncio.sleep(0.1)  # Reduced sleep for more frequent updates



def auto_control():
    """Automatically control LEDs based on Bluetooth beacon's RSSI."""
    global latest_rssi, last_valid_rssi, should_continue
    previous_intensity = 0
    while should_continue:
        # Use the latest RSSI value, or the last valid RSSI if no new value is available
        rssi_value = latest_rssi if latest_rssi is not None else last_valid_rssi
        if rssi_value is not None:
            # Map the RSSI value to the intensity
            rssi_intensity = map_value(rssi_value, rssi_min, rssi_max, min_intensity, max_intensity)
            # Dampen the intensity change to reduce abrupt changes
            dampened_intensity = previous_intensity * 0.7 + rssi_intensity * 0.3
            previous_intensity = dampened_intensity
            print(f"RSSI: {rssi_value}, Mapped Intensity: {rssi_intensity:.2f}, Dampened Intensity: {dampened_intensity:.2f}")
            adjust_led_intensity(rssi_value, dampened_intensity)
        time.sleep(0.05)  # Adjust for desired responsiveness

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
