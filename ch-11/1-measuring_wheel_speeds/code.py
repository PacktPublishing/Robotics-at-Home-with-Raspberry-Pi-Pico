import asyncio
import board
import busio
import robot
uart = busio.UART(board.GP12, board.GP13, baudrate=9600)

class Settings:
  speed = 0.7
  time_interval = 0.2

async def motor_speed_loop():
  left_last, right_last = robot.left_encoder.read(), robot.right_encoder.read()
  while True:
    await asyncio.sleep(Settings.time_interval)
    left_new, right_new = robot.left_encoder.read(), robot.right_encoder.read()
    left_speed = robot.ticks_to_mm(left_new - left_last) / Settings.time_interval
    left_last = left_new
    right_speed = robot.ticks_to_mm(right_new - right_last) / Settings.time_interval
    right_last = right_new
    uart.write(f"{left_speed:.3f},{right_speed:.3f},0\n".encode())

async def stop_motors_after(seconds):
  await asyncio.sleep(seconds)
  robot.stop()

async def command_handler():
  while True:
    if uart.in_waiting:
      command = uart.readline().decode().strip()
      if command.startswith("M"):
        speed = float(command[1:])
      elif command.startswith("T"):
        Settings.time_interval = float(command[1:])
      elif command == "O":
        robot.stop()
      elif command.startswith("O"):
        robot.set_left(Settings.speed)
        robot.set_right(Settings.speed)
        asyncio.create_task(stop_motors_after(float(command[1:])))
      elif command.startswith("?"):
        uart.write(f"M{Settings.speed:.1f}\n".encode())
        uart.write(f"T{Settings.time_interval:.1f}\n".encode())
        await asyncio.sleep(3)
    await asyncio.sleep(0)

asyncio.create_task(motor_speed_loop())
asyncio.run(command_handler())
