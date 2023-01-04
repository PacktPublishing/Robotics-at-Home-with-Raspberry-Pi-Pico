import robot
import pid_controller
import asyncio
import time

# PID Loop control for IMU face north
class FaceNorthController:
    def __init__(self):
        self.pid = pid_controller.PIDController(0.01, 0.010, 0)
        self.target = 0

    def update(self, dt, angle):
        error = self.target - angle
        if error > 180:
            error -= 360
        elif error < -180:
            error += 360
        control_signal = self.pid.calculate(error, dt)
        robot.set_left(control_signal)
        robot.set_right(-control_signal)

async def control_loop():
  controller = FaceNorthController()
  last_time = time.monotonic()
  while True:
    await asyncio.sleep(0.1)
    next_time = time.monotonic()
    dt = next_time - last_time
    last_time = next_time
    angle = robot.imu.euler[0]

    controller.update(dt, angle)
    robot.send_line(f"{angle}, 0")


async def main():
  while not robot.check_imu_status():
    await asyncio.sleep(0.1)

  robot.send_line("Ready to go!")
  # Wait for start signal
  while True:
    if robot.uart.in_waiting:
      command = robot.uart.readline().decode().strip()
      if command == "start":
        break
    await asyncio.sleep(0.1)

  await control_loop()

print("Starting")
asyncio.run(main())
