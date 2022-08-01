import time
import board
import busio
import robot
from pid_controller import PIDController

uart = busio.UART(board.GP12, board.GP13, baudrate=9600)


robot.right_distance.distance_mode = 1
robot.right_distance.start_ranging()

speed = 0.7
distance_set_point = 15
distance_controller = PIDController(0.046, 0.0, 0)
print("Waiting for bytes on UART...")

prev_time = time.monotonic()
motors_active = False
while True:
  if robot.right_distance.data_ready:
    distance = robot.right_distance.distance
    error = distance_set_point - distance

    current_time = time.monotonic()
    deflection = distance_controller.calculate(error, current_time - prev_time)
    prev_time = current_time
    uart.write(f"{error},{deflection}\n".encode()) # ,{distance_controller.derivative}
    if motors_active:
      robot.set_left(speed - deflection)
      robot.set_right(speed + deflection)
    # reset the distance sensor
    robot.right_distance.clear_interrupt()
    time.sleep(0.05)
  if uart.in_waiting:
    command = uart.readline().decode().strip()
    if command.startswith("M"):
      speed = float(command[1:])
    elif command == "O":
      motors_active = not motors_active
      robot.set_left(0)
      robot.set_right(0)
      distance_controller.integral = 0
    elif command.startswith("P"):
      distance_controller.kp = float(command[1:])
    elif command.startswith("I"):
      distance_controller.ki = float(command[1:])
    elif command.startswith("D"):
      distance_controller.kd = float(command[1:])
    elif command.startswith("S"):
      distance_set_point = float(command[1:])
    elif command.startswith("?"):
      uart.write(f"P{distance_controller.kp:.3f}\n".encode())
      uart.write(f"I{distance_controller.ki:.3f}\n".encode())
      uart.write(f"D{distance_controller.kd:.3f}\n".encode())
      uart.write(f"S{distance_set_point:.3f}\n".encode())
      uart.write(f"M{speed:.1f}\n".encode())
      time.sleep(3)
    elif command.startswith("R"):
      distance_controller.integral = 0
