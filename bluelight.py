import asyncio
import threading
from gpiozero import PWMOutputDevice
from bleak import BleakScanner

# Set up the GPIO for the LED
pin = PWMOutputDevice(18)

# Default intensity when beacon is not detected (range 0 to 1)
default_intensity = 0.0  # Off when not detected

# Global variable to hold the latest RSSI value
latest_rssi = None

def map_value(x, in_min, in_max, out_min, out_max):
    """Map a value from one range to another."""
    x = max(min(x, in_max), in_min)
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def adjust_led_intensity(intensity):
    """Adjust LED intensity based on the mapped value."""
    pin.value = intensity

def auto_control():
    """Automatically control LED based on Bluetooth beacon's RSSI to represent signal strength."""
    global latest_rssi
    while True:
        intensity = default_intensity
        if latest_rssi is not None:
            # Intensity increases as RSSI gets stronger (closer)
            intensity = map_value(latest_rssi, -85, -40, 0, 1)
            print(f"RSSI: {latest_rssi}, Mapped Intensity: {intensity:.2f}")

        intensity = max(0, min(1, intensity))  # Constrain to 0-1
        adjust_led_intensity(intensity)

async def rssi_scanning():
    """Asynchronous method to continuously scan for BLE devices and update RSSI."""
    global latest_rssi
    target_device_address = "C9:FA:4B:21:11:26"  # Replace with your device's MAC address

    while True:
        devices = await BleakScanner.discover(timeout=2.0)
        for device in devices:
            if device.address == target_device_address:
                latest_rssi = device.rssi
                break
        await asyncio.sleep(0.1)

def start_async_loop(loop):
    """Starts the asynchronous event loop."""
    asyncio.set_event_loop(loop)
    loop.run_until_complete(rssi_scanning())

def main():
    # Start the BLE RSSI scanning in a separate thread
    loop = asyncio.new_event_loop()
    threading.Thread(target=start_async_loop, args=(loop,), daemon=True).start()

    # Start the auto control thread
    threading.Thread(target=auto_control, daemon=True).start()

if __name__ == "__main__":
    main()
