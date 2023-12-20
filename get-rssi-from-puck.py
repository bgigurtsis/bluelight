import asyncio
from bleak import BleakScanner

async def run():
    target_device_name = "Puck.js"
    target_device_address = "C9:FA:4B:21:11:26"

    while True:
        devices = await BleakScanner.discover()
        found = False

        for device in devices:
            if device.name == target_device_name or device.address == target_device_address:
                advertisement_data = device.metadata['advertisement_data']
                rssi = advertisement_data.rssi
                print(f"Found {target_device_name}: Address={device.address}, RSSI={rssi}")
                found = True
                break

        if not found:
            print(f"{target_device_name} not found.")

        await asyncio.sleep(5)  # Delay in seconds before rescanning

loop = asyncio.get_event_loop()
loop.run_until_complete(run())
