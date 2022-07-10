import time
import board
import busio
import robot

uart = busio.UART(board.GP12, board.GP13, baudrate=9600)

class PController:
    def __init__(self, kp):
        self.kp = kp

    def calculate(self, error):
        return self.kp * error


## We'll set up a single distance sensor, and keep a set distance from an object
robot.left_distance.distance_mode = 1
robot.left_distance.start_ranging()

distance_set_point = 10
distance_controller = PController(-0.1)

while True:
  if robot.left_distance.data_ready:
    distance = robot.left_distance.distance
    error = distance_set_point - distance
    speed = distance_controller.calculate(error)
    uart.write(f"{error},{speed}\n".encode())
    print(f"{error},{speed}")
    robot.set_left(speed)
    robot.set_right(speed)
    robot.left_distance.clear_interrupt()
    time.sleep(0.05)
