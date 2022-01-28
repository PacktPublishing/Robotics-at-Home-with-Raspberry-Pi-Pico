import time
import robot

robot.set_left(0.8)
robot.set_right(0.8)
target = 4000

while robot.left_encoder.read() < target or robot.right_encoder.read() < target:
  if robot.left_encoder.read() >= target:
    robot.set_left(0)
  if robot.right_encoder.read() >= target:
    robot.set_right(0)
  print(robot.left_encoder.read(), robot.right_encoder.read())
