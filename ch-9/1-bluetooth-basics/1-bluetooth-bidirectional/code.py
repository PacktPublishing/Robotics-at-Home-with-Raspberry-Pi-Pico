import board 
import busio
import supervisor

# PICO UART pins? What am i not using?
uart = busio.UART(board.GP12,board.GP13,baudrate=9600, timeout=0.01)

print("Waiting for bytes on UART...")
while True:
    data = uart.read(32)
    if data is not None:
        print(data)
    if supervisor.runtime.serial_bytes_available:
        value = input().strip()
        print(f"Received: {value}\r")
        uart.write(value.encode())
