import board 
import busio

uart = busio.UART(board.GP12,board.GP13,baudrate=9600, timeout=0.01)

print("Waiting for bytes on UART...")
while True:
    if uart.in_waiting:
        print(uart.read(32))
