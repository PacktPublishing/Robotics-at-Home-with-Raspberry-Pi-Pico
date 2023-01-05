import asyncio
import time
import robot
import pid_controller

class Settings:
  speed = 0.17
  time_interval = 0.2
  motors_enabled = False


class SpeedController:
  def __init__(self, encoder, motor_fn):
    self.encoder = encoder
    self.motor_fn = motor_fn
    self.pid = pid_controller.PIDController(3, 0, 1)
    self.reset()

  def reset(self):
    self.last_ticks = self.encoder.read()
    self.pwm = 0
    self.actual_speed = 0
    self.pid.reset()

  def update(self, dt):
    current_ticks = self.encoder.read()
    speed_in_ticks = (current_ticks - self.last_ticks) / dt
    self.last_ticks = current_ticks
    self.actual_speed = robot.ticks_to_m * speed_in_ticks
    # calculate the error
    error = Settings.speed - self.actual_speed
    # calculate the control signal
    control_signal = self.pid.calculate(error, dt)
    self.pwm += control_signal
    self.motor_fn(self.pwm * Settings.motors_enabled)


left = SpeedController(robot.left_encoder, robot.set_left)
right = SpeedController(robot.right_encoder, robot.set_right)


async def motor_speed_loop():
  last_time = time.monotonic()
  while True:
    await asyncio.sleep(Settings.time_interval)
    current_time = time.monotonic()
    dt = current_time - last_time
    last_time = current_time
    left.update(dt)
    right.update(dt)
    robot.send_line(f"{left.actual_speed:.2f},{Settings.speed * Settings.motors_enabled:.2f},0")


async def stop_motors_after(seconds):
  await asyncio.sleep(seconds)
  Settings.motors_enabled = False


async def command_handler():
  while True:
    if robot.uart.in_waiting:
      command = robot.uart.readline().decode().strip()
      if command.startswith("M"):
        Settings.speed = float(command[1:])
      elif command.startswith("T"):
        Settings.time_interval = float(command[1:])
      elif command == "G":
        Settings.motors_enabled = False
      elif command.startswith("G"):
        await asyncio.sleep(5)
        asyncio.create_task(
          stop_motors_after(float(command[1:]))
        )
        Settings.motors_enabled = True
        left.reset()
        right.reset()
      elif command.startswith("?"):
        robot.send_line(f"M{Settings.speed:.1f}")
        robot.send_line(f"T{Settings.time_interval:.1f}")
        await asyncio.sleep(3)
    await asyncio.sleep(0)

try:
  motors_task = asyncio.create_task(motor_speed_loop())
  asyncio.run(command_handler())
finally:
  motors_task.cancel()
  robot.stop()
