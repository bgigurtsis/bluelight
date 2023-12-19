#!/usr/bin/env python3
import bluetooth
import bluetooth._bluetooth as bluez
import time
import sys

def get_connected_devices(sock):
    """Get a list of connected devices."""
    connected_devices = []
    max_rsp = 255
    mode = 0
    results, num_rsp = bluez.hci_inquiry(sock, length=8, max_rsp=max_rsp, flags=mode)

    for i in range(num_rsp):
        addr = results[i][0]
        name = bluetooth.lookup_name(addr)
        connected_devices.append((addr, name))
    
    return connected_devices

def get_rssi(sock, addr):
    """Get the RSSI of a specific connected device."""
    try:
        rssi = bluez.hci_read_rssi(sock, addr)
    except Exception as e:
        print("Could not read RSSI for", addr)
        print(e)
        return None
    return rssi

def main():
    dev_id = 0
    try:
        sock = bluez.hci_open_dev(dev_id)
        print("Bluetooth device opened successfully.")
    except Exception as e:
        print("Error accessing bluetooth device.")
        print(e)
        sys.exit(1)

    connected_devices = get_connected_devices(sock)
    if not connected_devices:
        print("No connected Bluetooth devices found.")
        return

    for addr, name in connected_devices:
        rssi = get_rssi(sock, addr)
        if rssi is not None:
            print(f"Device: {name} ({addr}), RSSI: {rssi}")

if __name__ == "__main__":
    main()
