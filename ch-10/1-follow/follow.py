import time
import robot
import pid

class FollowObject:
  def __init__(self):
    self.max_speed = 0.9
    self.follow_pid = pid.PID(0.1, 0.1, 0.015, 15)
    self.last_time = time.monotonic_ns()
    self.left_dist = 0
    self.pid_output = 0

  def setup_robot(self):
    robot.left_distance.distance_mode = 1

  def movement_update(self):
    # do we have data
    if robot.left_distance.data_ready:
      self.left_dist = robot.left_distance.distance
      
      # calculate time delta
      new_time = time.monotonic_ns()
      time_delta = new_time - self.last_time
      self.last_time = new_time

      # get speeds from pid
      self.pid_output = self.follow_pid.update(self.left_dist, time_delta)
      speed = min(self.max_speed, self.pid_output)
      speed = max(-self.max_speed, speed)

      # make movements
      robot.set_left(speed)
      robot.set_right(speed)

      # reset and loop
      robot.left_distance.clear_interrupt()

  def main_loop(self):
    robot.left_distance.start_ranging()
    self.last_time = time.monotonic()
    while True:
      self.movement_update()

  def start(self):
    print("Starting")
    try:
      self.setup_robot()
      self.main_loop()
    finally:
      robot.stop()
      robot.left_distance.clear_interrupt()
      robot.left_distance.stop_ranging()

FollowObject().start()
