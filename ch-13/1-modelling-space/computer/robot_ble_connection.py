import asyncio
import typing

import bleak


class BleConnection:
    # See https://learn.adafruit.com/introducing-adafruit-ble-bluetooth-low-energy-friend/uart-service
    ble_uuid = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
    adafruit_rx_uuid = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"
    adafruit_tx_uuid = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
    ble_name = "Adafruit Bluefruit LE"

    def __init__(self, receive_handler: typing.Callable[[bytes], None], 
            connected_handler: typing.Callable[[], None]):
        self.ble_client : bleak.BleakClient = None
        self.receive_handler = receive_handler
        self.connected_handler = connected_handler

    def _uart_handler(self, _, data: bytes):
        self.receive_handler(data)

    async def connect(self):
        print("Scanning for devices...")
        devices = await bleak.BleakScanner.discover(service_uuids=[self.ble_uuid])
        print(f"Found {len(devices)} devices")
        print([device.name for device in devices])        
        ble_device_info = [device for device in devices if device.name==self.ble_name][0]
        print("Connecting to {}...".format(ble_device_info.name))
        async with bleak.BleakClient(ble_device_info.address) as ble_client:
            self.ble_client = ble_client
            self.connected_handler()
            print("Connected to {}".format(ble_device_info.name))
            asyncio.create_task(
                self.ble_client.start_notify(self.adafruit_rx_uuid, self._uart_handler)
            )
            while True:
                await asyncio.sleep(1)

    def send_uart_data(self, data: bytes):
        if self.ble_client:
            asyncio.create_task(
                self.ble_client.write_gatt_char(self.adafruit_tx_uuid, data)
            )
