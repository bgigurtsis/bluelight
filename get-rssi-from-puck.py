import asyncio
from bleak import BleakScanner

async def run():
    target_device_name = "Puck.js"
    target_device_address = "C9:FA:4B:21:11:26"
    while True:
        devices = await BleakScanner.discover()
        found = False
        for d in devices:
            if d.name == target_device_name or d.address == target_device_address:
                print(f"Found {target_device_name}: Address={d.address}, RSSI={d.metadata['rssi']}")
                found = True
                break
        if not found:
            print(f"{target_device_name} not found.")
        await asyncio.sleep(1)  # Delay in seconds before rescanning

loop = asyncio.get_event_loop()
loop.run_until_complete(run())
