import board 
from digitalio import DigitalInOut
import time
import busio
import supervisor
import adafruit_bluefruit_connect.button_packet, adafruit_bluefruit_connect.quaternion_packet


led = DigitalInOut(board.LED)
led.switch_to_output()

# PICO UART pins? What am i not using?
uart = busio.UART(board.GP12,board.GP13,baudrate=9600, timeout=0.01)

print("Waiting for bytes on UART...")
while True:
    data = uart.read(32)
    if data is not None:
      if data[0] == b'!'[0]:
        print("Looks like a control packet")
        if data[1] == b'B'[0]:
          buttons = adafruit_bluefruit_connect.button_packet.ButtonPacket.from_bytes(data)
          print("Button:", buttons.button, "pressed:", buttons.pressed)
        elif data[1] == b'Q'[0]:
          quaternion = adafruit_bluefruit_connect.quaternion_packet.QuaternionPacket.from_bytes(data)
          print(f"Quaternion: {quaternion.w} + {quaternion.x}i + {quaternion.y}j + {quaternion.z}k")
        else:
          print("Data[1]:", data[1])
      else:
        print("Data[0]:", data[0])
        print(data)
    if supervisor.runtime.serial_bytes_available:
        value = input().strip()
        print(f"Received: {value}\r")
        uart.write(value.encode())
