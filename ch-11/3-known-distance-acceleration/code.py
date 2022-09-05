import asyncio
import time
import robot
import pid_controller


class DistanceController:
  def __init__(self, encoder, motor_fn):
    self.encoder = encoder
    self.motor_fn = motor_fn
    # accel
    # self.pid = pid_controller.PIDController(0.00000, 0,	0.00008, d_filter_gain=1) 
    self.pid = pid_controller.PIDController(0.00000, 0.0000,	0.00001, d_filter_gain=1) 
    self.start_ticks = self.encoder.read()
    self.pwm = 0
    self.error = 0

  def update(self, dt, expected, debug=False):
    actual = self.encoder.read() - self.start_ticks
    # calculate the error
    self.error = expected - actual

    # calculate the control signal
    control_signal = self.pid.calculate(self.error, dt)
    print(control_signal)
    # self.pwm += control_signal
    if debug:
      robot.uart.write(f"0, {expected:.2f},{actual:.2f}\n".encode())
    # self.motor_fn(self.pwm)
    self.motor_fn(control_signal)

class DistanceTracker:
  def __init__(self):
    self.speed = 0.10
    self.time_interval = 0.2
    self.reset()

  def reset(self):
    self.start_time = time.monotonic()
    self.total_distance_in_ticks = 0
    self.total_time = 0.1

  def set_distance(self, new_distance):
    self.reset()
    self.total_distance_in_ticks = robot.mm_to_ticks(new_distance * 1000)
    self.total_time = new_distance / self.speed

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
      expected = time_proportion * self.total_distance_in_ticks
      left.update(dt, expected, debug=True)
      right.update(dt, expected)


distance_tracker = DistanceTracker()


async def command_handler():
  while True:
    if robot.uart.in_waiting:
      command = robot.uart.readline().decode().strip()
      # PID settings
      if command.startswith("M"):
        distance_tracker.speed = float(command[1:])
      elif command.startswith("T"):
        distance_tracker.time_interval = float(command[1:])
      # Start/stop commands
      elif command == "O":
        distance_tracker.set_distance(0)
      elif command.startswith("O"):
        await asyncio.sleep(5)
        distance_tracker.set_distance(float(command[1:]))
      # Print settings
      elif command.startswith("?"):
        robot.uart.write(f"M{distance_tracker.speed:.1f}\n".encode())
        robot.uart.write(f"T{distance_tracker.time_interval:.1f}\n".encode())
        await asyncio.sleep(3)
    await asyncio.sleep(0)

try:
  asyncio.create_task(distance_tracker.loop())
  asyncio.run(command_handler())
finally:
  robot.stop()
