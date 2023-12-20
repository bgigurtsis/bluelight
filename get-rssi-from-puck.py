import asyncio
from bleak import BleakScanner

device_address = "C9:FA:4B:21:11:26"  # MAC address of Puck.js

async def discover_device_rssi(address):
    devices = await BleakScanner.discover()
    for device in devices:
        if device.address == address:
            print(f"Device {device.address} RSSI: {device.rssi}")
            return
    print("Device not found.")

asyncio.run(discover_device_rssi(device_address))
