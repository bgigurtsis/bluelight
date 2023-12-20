import asyncio
from bleak import BleakClient

async def get_rssi(device_address):
    async with BleakClient(device_address) as client:
        is_connected = await client.is_connected()
        if is_connected:
            return client.last_rssi
        else:
            print("Failed to connect to the device.")
            return None

def main():
    device_address = "C9:FA:4B:21:11:26"  # Hardcoded MAC address of Puck.js
    rssi = asyncio.run(get_rssi(device_address))

    if rssi is not None:
        print(f"Device {device_address} RSSI: {rssi}")
    else:
        print("RSSI could not be retrieved.")

if __name__ == "__main__":
    main()
