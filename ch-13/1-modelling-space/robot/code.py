import asyncio
import json

import arena
import robot


async def command_handler():
  while True:
    if robot.uart.in_waiting:
      print("Receiving data...")
      data = robot.uart.readline().decode()
      print(f"Received data: {data}")
      request = json.loads(data)
      print(f"Received command: {request}")
      # {"command": "arena"}
      if request["command"] == "arena":
         response = {
            "arena": arena.boundary_lines,
            "target_zone": arena.target_zone,
         }
         robot.uart.write((json.dumps(response)+"\n").encode())

asyncio.run(command_handler())
