import board 
from digitalio import DigitalInOut
import time
import busio

led = DigitalInOut(board.LED)
led.switch_to_output()

# PICO UART pins? What am i not using?
uart = busio.UART(board.GP12,board.GP13,baudrate=9600)

while True:
    data = uart.read(32)
    
    if data is not None:
        print(data)
        data_string = ''.join([chr(b) for b in data])
        if data_string=='1':
            led.value = True
            uart.write('on')
        if data_string=='0':
            led.value = False
            uart.write('off')
