import asyncio
import json

import arena
import robot

def send_json(data):
  robot.uart.write((json.dumps(data)+"\n").encode())


async def command_handler():
  while True:
    if robot.uart.in_waiting:
      print("Receiving data...")
      try:
        data = robot.uart.readline().decode()
        request = json.loads(data)
      except (UnicodeError, ValueError):
        print("Invalid data")
        continue
      # {"command": "arena"}
      if request["command"] == "arena":
         send_json({
            "arena": arena.boundary_lines,
            "target_zone": arena.target_zone,
         })
    await asyncio.sleep(0.1)

asyncio.run(command_handler())
