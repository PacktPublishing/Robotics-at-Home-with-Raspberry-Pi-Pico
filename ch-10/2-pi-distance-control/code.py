import time
import board
import busio
import robot

uart = busio.UART(board.GP12, board.GP13, baudrate=9600)

class PIController:
    def __init__(self, kp, ki):
        self.kp = kp
        self.ki = ki
        self.integral = 0

    def calculate(self, error, dt):
        self.integral += error * dt
        return self.kp * error + self.ki * self.integral


## We'll set up a single distance sensor, and keep a set distance from an object
robot.right_distance.distance_mode = 1
robot.right_distance.start_ranging()

distance_set_point = 10
distance_controller = PIController(-0.19, -0.005)

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
    uart.write(f"{error},{speed},"
      f"{distance_controller.integral}\n".encode())
    print(f"{error},{speed},{distance_controller.integral}")
    robot.set_left(speed)
    robot.set_right(speed)
    robot.right_distance.clear_interrupt()
    time.sleep(0.05)
