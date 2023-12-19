import subprocess
import re

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
    rssi = re.search(r'RSSI return value: (-\d+)', output)
    return int(rssi.group(1)) if rssi else None

def main():
    devices = get_connected_devices()
    if devices:
        for device in devices:
            rssi = get_rssi(device)
            print(f"Device {device} RSSI: {rssi}")
    else:
        print("No connected Bluetooth devices found.")

if __name__ == "__main__":
    main()
