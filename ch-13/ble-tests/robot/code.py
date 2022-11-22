import board
import busio
import time
uart = busio.UART(board.GP12, board.GP13, baudrate=9600)


while True:
  while uart.in_waiting:
      print("Receiving data...")
      data = uart.readline()
      print(f"Received {data.decode()}")
      uart.write(f"Received {len(data)} bytes\n".encode())
  time.sleep(0.1)
