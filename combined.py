import bluetooth
import sys
import time

def find_device_address(device_name):
    nearby_devices = bluetooth.discover_devices(duration=8, lookup_names=True, flush_cache=True, lookup_class=False)
    for addr, name in nearby_devices:
        if device_name == name:
            return addr
    return None

def get_device_rssi(target_address):
    # Create a Bluetooth socket and connect to the device
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    try:
        sock.connect((target_address, 1))
    except bluetooth.btcommon.BluetoothError as err:
        print(f"Cannot connect to the Bluetooth device: {err}")
        return None

    # The RSSI can typically be read from the socket, but this is hardware and stack dependent
    rssi = None
    try:
        rssi = sock.getsockopt(bluetooth.SOL_RFCOMM, bluetooth.RFCOMM_LM)
    except Exception as e:
        print(f"Error getting RSSI: {e}")

    sock.close()
    return rssi

# Replace with the name of your Bluetooth device
device_name = "Your_Device_Name"

# Find the device by name
device_address = find_device_address(device_name)
if device_address is None:
    print(f"Device {device_name} not found")
    sys.exit(1)

# Get the RSSI of the connected device
rssi = get_device_rssi(device_address)
if rssi is not None:
    print(f"RSSI of the device {device_name} ({device_address}): {rssi}")
else:
    print("Could not read RSSI")
