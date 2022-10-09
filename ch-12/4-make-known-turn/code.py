import robot
import pid_controller
import asyncio
import time

class IMUTurnController:
    def __init__(self):
        self.pid = pid_controller.PIDController(0.01, 0.008, 0)
        self.target = 0
        self.error = 0

    def update(self, dt, angle):
        error = self.target - angle
        if error > 180:
            error -= 360
        elif error < -180:
            error += 360
        self.error = error
        control_signal = self.pid.calculate(error, dt)
        robot.set_left(control_signal)
        robot.set_right(-control_signal)


async def command_handler(turn_controller):
  while True:
    if robot.uart.in_waiting:
      command = robot.uart.readline().decode().strip()
      if command.startswith("-"):
        turn_controller.target -= int(command.lstrip('-'))
      elif command.startswith("+"):
        turn_controller.target += int(command.lstrip('+'))
      elif command.isdigit():
        turn_controller.target += int(command)
    await asyncio.sleep(0)


# control loop
async def control_loop():
  controller = IMUTurnController()
  controller.target = robot.imu.euler[0]
  asyncio.create_task(command_handler(controller))
  last_time = time.monotonic()
  while True:
    await asyncio.sleep(0.1)
    next_time = time.monotonic()
    dt = next_time - last_time
    last_time = next_time
    angle = robot.imu.euler[0]

    controller.update(dt, angle)
    robot.uart.write(f"{controller.error}, 0\n".encode())


async def main():
  while not robot.check_imu_status():
    await asyncio.sleep(0.1)
  robot.uart.write("Ready to go!\n".encode())

  await control_loop()

asyncio.run(main())
