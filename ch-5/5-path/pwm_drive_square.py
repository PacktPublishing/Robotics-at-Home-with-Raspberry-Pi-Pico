import time
import robot

def straight(speed, duration):
    robot.set_left(speed)
    robot.set_right(speed)
    time.sleep(duration)

def left(speed, duration):
    robot.set_left(0)
    robot.set_right(speed)
    time.sleep(duration)

try:
    for n in range(0, 4):
        straight(0.6, 1.0)
        left(0.6, 1)
finally:
    robot.stop()

