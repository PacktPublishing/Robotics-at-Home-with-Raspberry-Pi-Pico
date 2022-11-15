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
  
  async def run(self):
    try:
      for _ in range(3):
        encoder_left = robot.left_encoder.read()
        encoder_right = robot.right_encoder.read()
        robot.set_left(0.5)
        robot.set_right(0.5)
        await asyncio.sleep(0.1)
        left_movement = robot.left_encoder.read() - encoder_left
        right_movement = robot.right_encoder.read() - encoder_right
        speed_in_mm = robot.ticks_to_m * ((left_movement + right_movement) / 2) * 1000
        for pose in self.poses:
          pose[0] += speed_in_mm * np.cos(np.radians(pose[2]))
          pose[1] += speed_in_mm * np.sin(np.radians(pose[2]))
    finally:
      robot.stop()

def send_json(data):
  robot.uart.write((json.dumps(data)+"\n").encode())

async def command_handler(simulation):
  simulation_task = None
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
      elif request["command"] == "start":
        print("Starting simulation")
        if simulation_task is None or simulation_task.done():
          simulation_task = asyncio.create_task(simulation.run())
      elif request["command"] == "stop":
        robot.stop()
        if simulation_task and not simulation_task.done():
          simulation_task.cancel()
          simulation_task = None
    else:
      send_json({
        "poses": simulation.poses.tolist(),
      })
    await asyncio.sleep(0.1)

simulation= Simulation()
asyncio.run(command_handler(simulation))
