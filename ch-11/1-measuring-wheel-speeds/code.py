import asyncio
import robot

class Settings:
  speed = 0.7
  time_interval = 0.2

async def motor_speed_loop():
  left_last, right_last = robot.left_encoder.read(), robot.right_encoder.read()
  while True:
    await asyncio.sleep(Settings.time_interval)
    left_new, right_new = robot.left_encoder.read(), robot.right_encoder.read()
    left_speed = robot.ticks_to_m * (left_new - left_last) / Settings.time_interval
    left_last = left_new
    right_speed = robot.ticks_to_m * (right_new - right_last) / Settings.time_interval
    right_last = right_new
    robot.send_line(f"{left_speed:.2f},{right_speed:.2f},0")

async def stop_motors_after(seconds):
  await asyncio.sleep(seconds)
  robot.stop()

async def command_handler():
  while True:
    if robot.uart.in_waiting:
      command = robot.uart.readline().decode().strip()
      if command.startswith("M"):
        Settings.speed = float(command[1:])
      elif command.startswith("T"):
        Settings.time_interval = float(command[1:])
      elif command == "G":
        robot.stop()
      elif command.startswith("G"):
        await asyncio.sleep(5)
        asyncio.create_task(
          stop_motors_after(float(command[1:]))
        )
        robot.set_left(Settings.speed)
        robot.set_right(Settings.speed)
      elif command.startswith("?"):
        robot.send_line(f"M{Settings.speed:.1f}")
        robot.send_line(f"T{Settings.time_interval:.1f}")
        await asyncio.sleep(3)
    await asyncio.sleep(0)

asyncio.create_task(motor_speed_loop())
asyncio.run(command_handler())
