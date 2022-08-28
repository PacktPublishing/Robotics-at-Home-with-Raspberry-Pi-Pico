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
    self.pid = pid_controller.PIDController(0, 6, 0)
    self.reset()

  def reset(self):
    self.last_ticks = self.encoder.read()
    self.error = 0
    self.control_signal = 0
    self.pid.reset()

  def update(self, dt):
    current_ticks = self.encoder.read()
    speed_in_ticks = (current_ticks - self.last_ticks) / dt
    self.last_ticks = current_ticks
    speed_in_m_per_s = robot.ticks_to_mm(speed_in_ticks) / 1000
    # calculate the error  
    self.error = (Settings.speed * Settings.motors_enabled) - speed_in_m_per_s
    # calculate the control signal
    self.control_signal = self.pid.calculate(self.error, dt)
    self.motor_fn(self.control_signal)
    

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
    robot.uart.write(f"0, {left.error:.2f},{right.error:.2f}\n".encode())


async def stop_motors_after(seconds):
  await asyncio.sleep(seconds)
  Settings.motors_enabled = False


async def command_handler():
  while True:
    if robot.uart.in_waiting:
      command = robot.uart.readline().decode().strip()
      # PID settings
      if command.startswith("P"):
        left.pid.kp = float(command[1:])
        right.pid.kp = float(command[1:])
      elif command.startswith("I"):
        left.pid.ki = float(command[1:])
        left.pid.reset()
        right.pid.ki = float(command[1:])
        right.pid.reset()
      elif command.startswith("D"):
        left.pid.kd = float(command[1:])
        right.pid.kd = float(command[1:])
      elif command.startswith("T"):
        Settings.time_interval = float(command[1:])
      # Speed settings
      elif command.startswith("M"):
        Settings.speed = float(command[1:])
      # Start/stop commands
      elif command == "O":
        Settings.motors_enabled = False
      elif command.startswith("O"):
        await asyncio.sleep(5)
        asyncio.create_task(stop_motors_after(float(command[1:])))
        Settings.motors_enabled = True
        left.reset()
        right.reset()
      # Print settings
      elif command.startswith("?"):
        robot.uart.write(f"M{Settings.speed:.1f}\n".encode())
        robot.uart.write(f"P{left.pid.kp:.2f}:I{left.pid.ki:.2f}:D{left.pid.kd:.2f}\n".encode())
        robot.uart.write(f"T{Settings.time_interval:.1f}\n".encode())
        await asyncio.sleep(3)
    await asyncio.sleep(0)

try:
  asyncio.create_task(motor_speed_loop())
  asyncio.run(command_handler())
finally:
  robot.stop()
