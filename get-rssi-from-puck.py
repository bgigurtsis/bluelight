from bluepy import btle

def get_rssi():
    device_address = "C9:FA:4B:21:11:26"  # Hardcoded MAC address of the Puck.js
    try:
        # Connect to the device
        peripheral = btle.Peripheral(device_address, "random")
        # Get RSSI
        rssi = peripheral.rssi
        # Disconnect
        peripheral.disconnect()
        return rssi
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    rssi = get_rssi()
    if rssi is not None:
        print(f"Device {device_address} RSSI: {rssi}")
    else:
        print("Failed to retrieve RSSI.")

if __name__ == "__main__":
    main()
