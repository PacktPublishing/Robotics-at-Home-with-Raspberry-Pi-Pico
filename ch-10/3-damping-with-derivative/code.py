import time
import board
import busio
import robot
from pid_controller import PIDController

uart = busio.UART(board.GP12, board.GP13, baudrate=9600)


## We'll set up a single distance sensor, and keep a set distance from an object
robot.right_distance.distance_mode = 1
robot.right_distance.start_ranging()

distance_set_point = 10
distance_controller = PIDController(-0.09, -0.02, -0.07)

prev_time = time.monotonic()
while True:
  if robot.right_distance.data_ready:
    distance = robot.right_distance.distance
    error = distance_set_point - distance

    current_time = time.monotonic()
    speed = distance_controller.calculate(error, current_time - prev_time)
    prev_time = current_time
    # Control the motors with the speed
    if abs(speed) < 0.3:
      speed = 0
    uart.write(f"{error},{speed},{distance_controller.integral},{distance_controller.derivative}\n".encode())
    print(f"{error},{speed},{distance_controller.integral},{distance_controller.derivative}")
    robot.set_left(speed)
    robot.set_right(speed)
    # reset the distance sensor
    robot.right_distance.clear_interrupt()
    time.sleep(0.05)
