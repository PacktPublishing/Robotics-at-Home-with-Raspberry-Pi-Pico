import board 
import busio

uart = busio.UART(board.GP12, board.GP13, baudrate=9600)

while True:
    if uart.read(32) is not None:
        uart.write("Hello, Bluetooth World!\n".encode())
