import board 
from digitalio import DigitalInOut
import time
import busio
import supervisor

led = DigitalInOut(board.LED)
led.switch_to_output()

# PICO UART pins? What am i not using?
uart = busio.UART(board.GP12,board.GP13,baudrate=9600)

while True:
    data = uart.read(32)
    if supervisor.runtime.serial_bytes_available:
        value = input().strip()
        print(f"Received: {value}\r")
        uart.write(value.encode())
    if data is not None:
        print(data)
