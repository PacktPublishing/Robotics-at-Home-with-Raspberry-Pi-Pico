import asyncio
import json

import arena
import robot


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
         response = {
            "arena": arena.boundary_lines,
            "target_zone": arena.target_zone,
         }
         robot.uart.write((json.dumps(response)+"\n").encode())
    await asyncio.sleep(0.1)

asyncio.run(command_handler())
