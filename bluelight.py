import asyncio
import threading
from gpiozero import PWMOutputDevice
from bleak import BleakScanner

# Set up the GPIO for the LED
pin = PWMOutputDevice(18)

# Default intensity when beacon is not detected (range 0 to 1)
default_intensity = 0.0

# Global variable to hold the latest RSSI value
latest_rssi = None
should_continue = True

def adjust_led_intensity(intensity):
    """Adjust LED intensity based on the mapped value."""
    pin.value = intensity

async def rssi_scanning():
    """Asynchronous method to continuously scan for BLE devices and update RSSI."""
    global latest_rssi, should_continue
    target_device_address = "C9:FA:4B:21:11:26"

    while should_continue:
        devices = await BleakScanner.discover(timeout=2.0)
        for device in devices:
            if device.address == target_device_address:
                latest_rssi = device.rssi
                break
        await asyncio.sleep(0.1)

def auto_control():
    """Automatically control LED based on Bluetooth beacon's RSSI."""
    global latest_rssi, should_continue
    while should_continue:
        intensity = default_intensity
        if latest_rssi is not None:
            # Modify this mapping as needed
            intensity = (latest_rssi + 85) / (-40 + 85)
            print(f"RSSI: {latest_rssi}, Intensity: {intensity:.2f}")

        adjust_led_intensity(max(0, min(1, intensity)))
        time.sleep(0.1)

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
