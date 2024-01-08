import asyncio
from bleak import BleakScanner

async def run():
    target_device_name = "Puck.js"
    target_device_address = "C9:FA:4B:21:11:26"

    while True:
        discovered = await BleakScanner.discover(timeout=1, return_adv=True)
        for address, (device, advertisement_data) in discovered.items():
            if device.name == target_device_name or device.address == target_device_address:
                rssi = advertisement_data.rssi
                print(f"Found {target_device_name}: Address={device.address}, RSSI={rssi}")
                break
        else:
            print(f"{target_device_name} not found.")


loop = asyncio.get_event_loop()
loop.run_until_complete(run())
