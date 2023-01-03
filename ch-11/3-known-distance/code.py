import asyncio
import time
import robot
import pid_controller


class DistanceController:
  def __init__(self, encoder, motor_fn):
    self.encoder = encoder
    self.motor_fn = motor_fn
    self.pid = pid_controller.PIDController(3.25, 0.5,	0.5, d_filter_gain=1) 
    self.start_ticks = self.encoder.read()
    self.error = 0

  def update(self, dt, expected):
    self.actual = self.encoder.read() - self.start_ticks
    # calculate the error
    self.error = (expected - self.actual) / robot.ticks_per_revolution
    # calculate the control signal
    control_signal = self.pid.calculate(self.error, dt)
    self.motor_fn(control_signal)
 
class DistanceTracker:
  def __init__(self):
    self.speed = 0.17
    self.time_interval = 0.2
    self.start_time = time.monotonic()
    self.current_position = 0
    self.total_distance_in_ticks = 0
    self.total_time = 0.1

  def set_distance(self, new_distance):
    # add the last travelled distance to the current position
    self.current_position += self.total_distance_in_ticks
    # calculate the new additional distance
    self.total_distance_in_ticks = robot.m_to_ticks * new_distance
    self.total_time = max(0.1, abs(new_distance / self.speed))
    self.start_time = time.monotonic()

  async def loop(self):
    left = DistanceController(robot.left_encoder, robot.set_left)
    right = DistanceController(robot.right_encoder, robot.set_right)
    last_time = time.monotonic()
    while True:
      await asyncio.sleep(self.time_interval)
      current_time = time.monotonic()
      dt = current_time - last_time
      last_time = current_time
      elapsed_time = current_time - self.start_time
      time_proportion = min(1, elapsed_time / self.total_time)
      expected = time_proportion * self.total_distance_in_ticks + self.current_position
      left.update(dt, expected)
      right.update(dt, expected)
      robot.send_line(f"{expected:.2f},{left.actual:.2f},0")


distance_tracker = DistanceTracker()


async def command_handler():
  while True:
    if robot.uart.in_waiting:
      command = robot.uart.readline().decode().strip()
      if command.startswith("M"):
        distance_tracker.speed = float(command[1:])
      elif command.startswith("T"):
        distance_tracker.time_interval = float(command[1:])
      elif command == "G":
        distance_tracker.set_distance(0)
      elif command.startswith("G"):
        await asyncio.sleep(5)
        distance_tracker.set_distance(float(command[1:]))
      elif command.startswith("?"):
        robot.send_line(f"M{distance_tracker.speed:.1f}")
        robot.send_line(f"T{distance_tracker.time_interval:.1f}")
        await asyncio.sleep(3)
    await asyncio.sleep(0)
    
try:
  motors_task = asyncio.create_task(distance_tracker.loop())
  asyncio.run(command_handler())
finally:
  motors_task.cancel()
  robot.stop()
