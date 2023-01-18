import time
import robot

robot.set_left(0.8)
robot.set_right(0.8)

time.sleep(1)
robot.stop()
print(robot.left_encoder.read(), robot.right_encoder.read())
