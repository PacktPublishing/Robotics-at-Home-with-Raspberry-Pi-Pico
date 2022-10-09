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


# control loop
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
    robot.uart.write(f"{angle}, 0\n".encode())

# main
async def main():
  await control_loop()

def check_status():
  sys_status, gyro, accel, mag = robot.imu.calibration_status
  print(f"Sys: {sys_status}, Gyro: {gyro}, Accel: {accel}, Mag: {mag}")
  robot.uart.write(f"Sys: {sys_status}, Gyro: {gyro}, Accel: {accel}, Mag: {mag}\n".encode())
  return sys_status == 3


while not check_status():
  time.sleep(0.1)

print("Ready to go!")
robot.uart.write("Ready to go!\n".encode())
# Wait for start signal
while True:
  if robot.uart.in_waiting:
    command = robot.uart.readline().decode().strip()
    if command == "start":
      break
    else:
      print("Unknown command: {}".format(command))
  time.sleep(0.1)

asyncio.run(main())
