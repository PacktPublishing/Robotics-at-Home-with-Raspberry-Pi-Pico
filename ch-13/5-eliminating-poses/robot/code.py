import asyncio
import json
import random
from ulab import numpy as np

import arena
import robot

class Simulation:
  def __init__(self):
    population_size = 10
    # x, y, heading
    self.poses = np.empty((population_size, 3), dtype=np.float)
    for n in range(population_size):
      self.poses[n] = random.uniform(0, arena.width), random.uniform(0, arena.height), random.uniform(0, 360)
  
  def move_poses(self, speed_in_mm, heading_change):
    for pose in self.poses:
      pose[2] += heading_change
      pose[2] = pose[2] % 360
      pose[0] += speed_in_mm * np.cos(np.radians(pose[2]))
      pose[1] += speed_in_mm * np.sin(np.radians(pose[2]))

  def eliminate_impossible_poses(self, left_distance, right_distance):
    poses_to_keep = np.ones(len(self.poses), dtype=np.uint8)
    # todo: would reorganising these pose arrays let us better use ulab tools?
    for position, pose in enumerate(self.poses):
      # first those outside the arena
      keep = arena.point_is_inside_arena((pose[0], pose[1]))
      if keep:
        left_distance_point = pose[0] + robot.distance_sensor_from_middle + left_distance * np.cos(np.radians(pose[2])), pose[1] + left_distance * np.sin(np.radians(pose[2]))
        right_distance_point = pose[0] + robot.distance_sensor_from_middle + right_distance * np.cos(np.radians(pose[2])), pose[1] + right_distance * np.sin(np.radians(pose[2]))
        keep = arena.point_is_inside_arena(left_distance_point) and arena.point_is_inside_arena(right_distance_point)
      poses_to_keep[position] = int(keep)
    # apply the keep as a mask to the poses using ulab. - doesn't work in ulab.
    self.poses = np.array([item for item, keep in zip(self.poses, poses_to_keep) if keep])

  async def run(self):
    try:
      robot.left_distance.start_ranging()
      robot.right_distance.start_ranging()
      for _ in range(5):
        starting_heading = robot.imu.euler[0]
        encoder_left = robot.left_encoder.read()
        encoder_right = robot.right_encoder.read()
        robot.set_left(1)
        robot.set_right(0.5)
        await asyncio.sleep(0.1)
        left_movement = robot.left_encoder.read() - encoder_left
        right_movement = robot.right_encoder.read() - encoder_right
        # move poses
        speed_in_mm = robot.ticks_to_m * ((left_movement + right_movement) / 2) * 1000
        new_heading = robot.imu.euler[0]
        heading_change =  starting_heading - new_heading
        self.move_poses(speed_in_mm, heading_change)
        if robot.left_distance.data_ready and robot.right_distance.data_ready:
          left_distance = robot.left_distance.distance
          right_distance = robot.right_distance.distance
          self.eliminate_impossible_poses(left_distance, right_distance)
          robot.left_distance.clear_interrupt()
          robot.right_distance.clear_interrupt()
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
      sys_status, gyro, accel, mag = robot.imu.calibration_status
      if sys_status != 3:
        send_json({"imu_calibration": {
          "gyro": gyro,
          "accel": accel,
          "mag": mag,
          "sys": sys_status,
        }})
      else:
        send_json({
          "poses": simulation.poses.tolist(),
        })
    await asyncio.sleep(0.1)

simulation= Simulation()
asyncio.run(command_handler(simulation))
