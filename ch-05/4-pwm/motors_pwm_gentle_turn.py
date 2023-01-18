import time
import robot

try:
    robot.set_left(1.0)
    robot.set_right(0.5)
    time.sleep(1)
finally:
    robot.stop()
