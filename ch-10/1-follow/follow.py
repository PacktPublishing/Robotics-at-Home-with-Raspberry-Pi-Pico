import robot
import time
import pid

robot.left_distance.distance_mode = 1

max_speed = 0.9
set_point = 15

robot.left_distance.start_ranging()

follow_pid = pid.PID(0.1, 0, 0)
last_time = time.monotonic()
print("Starting")
try:
  while True:
    # do we have data
    if robot.left_distance.data_ready:
      left_dist = robot.left_distance.distance
      
      # get error value
      error_value = left_dist - set_point
      
      # calculate time delta
      new_time = time.monotonic()
      time_delta = new_time - last_time
      last_time = new_time

      # get speeds from pid
      speed = min(max_speed, follow_pid.update(error_value, time_delta))
      speed = max(-max_speed, speed)

      # make movements
      print(f"Dist: {left_dist}, Err: {error_value}, Speed: {speed}")
      robot.set_left(speed)
      robot.set_right(speed)

      # reset and loop
      robot.left_distance.clear_interrupt()
      time.sleep(0.1)

finally:
  robot.stop()
  robot.left_distance.clear_interrupt()
  robot.left_distance.stop_ranging()
