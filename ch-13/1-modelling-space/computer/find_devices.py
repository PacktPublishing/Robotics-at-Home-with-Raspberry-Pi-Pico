import asyncio
from robot_ble_connection import BleConnection

async def run():
    ble_connection = BleConnection()
    await ble_connection.connect()

asyncio.run(run())
