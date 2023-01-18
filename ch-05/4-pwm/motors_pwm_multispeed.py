import time
import robot

try:
    for speed in range(5, 10):
        robot.set_left(speed / 10)
        robot.set_right(speed / 10)
        time.sleep(0.3)
finally:
    robot.stop()
