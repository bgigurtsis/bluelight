from bluepy.btle import Scanner

def get_rssi_from_scan(device_address):
    scanner = Scanner()
    devices = scanner.scan(10.0)  # Scanning for 10 seconds

    for dev in devices:
        if dev.addr == device_address:
            return dev.rssi
    return None

def main():
    device_address = "C9:FA:4B:21:11:26"  # Hardcoded MAC address of the Puck.js
    rssi = get_rssi_from_scan(device_address)

    if rssi is not None:
        print(f"Device {device_address} RSSI: {rssi}")
    else:
        print("Puck.js not found.")

if __name__ == "__main__":
    main()
