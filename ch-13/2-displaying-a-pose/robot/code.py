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
    for n in range(3):
      encoder_left = robot.left_encoder.read()
      encoder_right = robot.right_encoder.read()
      robot.set_speed(0.3, 0.3)
      await asyncio.sleep(0.1)
      left_movement = robot.left_encoder.read() - encoder_left
      right_movement = robot.right_encoder.read() - encoder_right
      speed_in_mm = robot.ticks_to_m((left_movement + right_movement) / 2) / 1000
      for pose in self.poses:
        pose[0] += speed_in_mm * np.cos(np.radians(pose[2]))
        pose[1] += speed_in_mm * np.sin(np.radians(pose[2]))
        pose[2] += robot.ticks_to_degrees(left_movement - right_movement) / robot.wheel_separation_mm
        pose[2] = pose[2] % 360
    robot.set_speed(0, 0)

async def command_handler(simulation):
  simulation_task = None
  while True:
    if robot.uart.in_waiting:
      print("Receiving data...")
      try:
        data = robot.uart.readline().decode()
      except UnicodeError:
        print("Invalid data")
        continue
      print(f"Received data: {data}")
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
      elif request["command"] == "reset":
        simulation.__init__()
      elif request["command"] == "run":
        simulation_task = asyncio.create_task(simulation.run())
      elif request["command"] == "stop":
        robot.set_speed(0, 0)
        if simulation_task:
          simulation_task.cancel()
          simulation_task = None
    else:
      response = {
        "poses": simulation.poses.tolist(),
      }
      robot.uart.write((json.dumps(response)+"\n").encode())
    await asyncio.sleep(0.1)

simulation= Simulation()
asyncio.run(command_handler(simulation))
