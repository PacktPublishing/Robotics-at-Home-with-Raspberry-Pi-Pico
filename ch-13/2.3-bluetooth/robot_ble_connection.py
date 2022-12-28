import asyncio

import bleak


class BleConnection:
    # See https://learn.adafruit.com/introducing-adafruit-ble-bluetooth-low-energy-friend/uart-service
    ble_uuid = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
    rx_gatt = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"
    tx_gatt = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
    ble_name = "Adafruit Bluefruit LE"

    def __init__(self, receive_handler):
        self.ble_client = None
        self.receive_handler = receive_handler

    def _uart_handler(self, _, data: bytes):
        self.receive_handler(data)

    async def connect(self):
        print("Scanning for devices...")
        devices = await bleak.BleakScanner.discover(
            service_uuids=[self.ble_uuid]
        )
        print(f"Found {len(devices)} devices")
        print([device.name for device in devices])        
        ble_device_info = [device for device in devices if device.name==self.ble_name][0]
        print(f"Connecting to {ble_device_info.name}...")
        self.ble_client = bleak.BleakClient(ble_device_info.address)
        await self.ble_client.connect()
        print("Connected to {}".format(ble_device_info.name))
        self.notify_task = asyncio.create_task(
            self.ble_client.start_notify(self.rx_gatt, self._uart_handler)
        )

    async def close(self):
        await self.ble_client.disconnect()
                
    async def send_uart_data(self, data):
        await self.ble_client.write_gatt_char(self.tx_gatt, data)
