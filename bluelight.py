import subprocess
import re

def get_connected_devices():
    try:
        # Running 'hcitool con' to get a list of connected devices
        hcitool_output = subprocess.check_output(['hcitool', 'con']).decode('utf-8')
        # Extracting device addresses using regular expression
        return re.findall(r'(?:>?\s)([0-9A-F:]{17})', hcitool_output)
    except subprocess.CalledProcessError:
        return []

def get_device_rssi(device_address):
    try:
        # Running 'btmgmt find' to get device information including RSSI
        btmgmt_output = subprocess.check_output(['sudo', 'btmgmt', 'find']).decode('utf-8')
        # Regular expression to find the RSSI for the specific device
        match = re.search(rf'{device_address}\s+.*\s+RSSI: (-?\d+)', btmgmt_output)
        if match:
            return int(match.group(1))
        return None
    except subprocess.CalledProcessError:
        return None

# Get list of connected Bluetooth devices
connected_devices = get_connected_devices()
print("Connected Bluetooth devices:")
for device in connected_devices:
    print(f"  Address: {device}")

    # Get RSSI for each connected device
    rssi = get_device_rssi(device)
    if rssi is not None:
        print(f"  RSSI: {rssi}")
    else:
        print("  RSSI: Not available")
