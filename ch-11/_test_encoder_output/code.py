import time
import board
import busio
import robot

uart = busio.UART(board.GP12, board.GP13, baudrate=9600)

speed = 0.7
stop_time = 0

while True:
  current_time = time.monotonic()
  if current_time > stop_time:
    robot.set_left(0)
    robot.set_right(0)
  left_value = robot.left_encoder.read()
  right_value = robot.right_encoder.read()
  uart.write(f"{left_value:.3f},{right_value:.3f}\n".encode() )
  time.sleep(0.02)
  if uart.in_waiting:
    command = uart.readline().decode().strip()
    if command.startswith("M"):
      speed = float(command[1:])
    elif command == "O":
      stop_time = 0
      robot.set_left(0)
      robot.set_right(0)
    elif command.startswith("O"):
      stop_time = float(command[1:]) + current_time
      robot.set_left(speed)
      robot.set_right(speed)
    elif command.startswith("?"):
      uart.write(f"M{speed:.1f}\n".encode())
      time.sleep(3)
