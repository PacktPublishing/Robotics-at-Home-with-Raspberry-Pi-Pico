import asyncio
from robot_ble_connection import BleConnection

def handle_data(data):
  print(f"Response: {data}")

async def main():
  ble_connection = BleConnection(handle_data)
  await ble_connection.connect()
  try:
      while True:
          await asyncio.sleep(0.5)
          await ble_connection.send_uart_data(bytes([65, 66, 13]))# "Hello World".encode())
          await asyncio.sleep(3)
          await ble_connection.send_uart_data("Hello\nwith newline in middle".encode())
          await asyncio.sleep(3)
          await ble_connection.send_uart_data("Hello with newline as end\n".encode())
          await asyncio.sleep(2.5)
  finally:
      await ble_connection.close()

asyncio.run(main())
