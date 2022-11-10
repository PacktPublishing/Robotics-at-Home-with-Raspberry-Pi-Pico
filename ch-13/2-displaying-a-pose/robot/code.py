import asyncio
import json
import random
from ulab import numpy as np

import arena
import robot

class Simulation:
  def __init__(self):
    population_size = 10
    self.poses = np.empty((population_size, 3), dtype=np.float)
    for n in range(population_size):
      self.poses[n] = random.uniform(0, arena.width), random.uniform(0, arena.height), random.uniform(0, 360)
  

async def command_handler(simulation):
  while True:
    if robot.uart.in_waiting:
      print("Receiving data...")
      try:
        data = robot.uart.readline().decode()
      except UnicodeError:
        print("Invalid data")
        continue
      try:
        request = json.loads(data)
        print(f"Received command: {request}")
      except ValueError:
        print("Invalid JSON")
        continue
      # {"command": "arena"}
      if request["command"] == "arena":
         response = {
            "arena": arena.boundary_lines,
            "target_zone": arena.target_zone,
         }
         robot.uart.write((json.dumps(response)+"\n").encode())
    else:
      response = {
        "poses": simulation.poses.tolist(),
      }
      robot.uart.write((json.dumps(response)+"\n").encode())
    await asyncio.sleep(0.1)

simulation= Simulation()
asyncio.run(command_handler(simulation))
