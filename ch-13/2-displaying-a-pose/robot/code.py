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
  
def send_json(data):
  robot.uart.write((json.dumps(data)+"\n").encode())

async def command_handler(simulation):
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
    else:
      send_json({
        "poses": simulation.poses.tolist(),
      })
    await asyncio.sleep(0.1)

simulation= Simulation()
asyncio.run(command_handler(simulation))
