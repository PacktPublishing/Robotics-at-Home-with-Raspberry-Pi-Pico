import asyncio
import bleak

async def run():
    ble_uuid = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
    ble_name = "Adafruit Bluefruit LE"
    devices = await bleak.BleakScanner.discover(service_uuids=[ble_uuid])
    print(f"Found {len(devices)} devices")
    print([device.name for device in devices])
    matching_devices = [device for device in devices if device.name==ble_name]
    if len(matching_devices) == 0:
        raise RuntimeError("Could not find robot")
    ble_device_info = matching_devices[0]
    print(f"Found robot {ble_device_info.name}...")

asyncio.run(run())
