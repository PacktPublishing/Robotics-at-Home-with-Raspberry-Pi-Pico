import asyncio
import json
import random
from ulab import numpy as np

import arena
import robot

class DistanceSensorTracker:
    def __init__(self):
        robot.left_distance.distance_mode = 2
        robot.right_distance.distance_mode = 2
        self.left = 300
        self.right = 300

    async def main(self):
        robot.left_distance.start_ranging()
        robot.right_distance.start_ranging()
        while True:
            if robot.left_distance.data_ready and robot.left_distance.distance:
                self.left = robot.left_distance.distance * 10  # convert to mm
                robot.left_distance.clear_interrupt()
            if robot.right_distance.data_ready and robot.right_distance.distance:
                self.right = robot.right_distance.distance * 10
                robot.right_distance.clear_interrupt()
            await asyncio.sleep(0.01)


class CollisionAvoid:
    def __init__(self, distance_sensors):
        self.speed = 0.6
        self.distance_sensors = distance_sensors

    async def main(self):
        while True:
            robot.set_right(self.speed)
            while self.distance_sensors.left < 300 or \
                    self.distance_sensors.right < 300:
                robot.set_left(-self.speed)
                await asyncio.sleep(0.3)
            robot.set_left(self.speed)
            await asyncio.sleep(0)


def send_json(data):
    robot.uart.write((json.dumps(data) + "\n").encode())

def read_json():
    try:
      data = robot.uart.readline()
      decoded = data.decode()
      return json.loads(decoded)
    except (UnicodeError, ValueError):
      print("Invalid data")
      return None


def send_poses(samples):
    send_json({
        "poses": np.array(samples[:,:2], dtype=np.int16).tolist(),
    })


class Simulation:
    def __init__(self):
      self.population_size = 20
      self.poses = np.array(
          [(
              int(random.uniform(0, arena.width)),
              int(random.uniform(0, arena.height)),
              int(random.uniform(0, 360))) for _ in range(self.population_size)],
          dtype=np.float,
      )
      self.distance_sensors = DistanceSensorTracker()
      self.collision_avoider = CollisionAvoid(self.distance_sensors)

    async def main(self):
        asyncio.create_task(self.distance_sensors.main())
        collision_avoider = asyncio.create_task(self.collision_avoider.main())
        try:
            while True:
                await asyncio.sleep(0.1)
                send_poses(self.poses)
        finally:
            collision_avoider.cancel()
            robot.stop()


async def command_handler(simulation):
    print("Starting handler")
    simulation_task = None
    while True:
        if robot.uart.in_waiting:
            request = read_json()
            if not request:
                continue
            print("Received: ", request)
            if request["command"] == "arena":
                send_json({
                    "arena": arena.boundary_lines,
                })
            elif request["command"] == "start":
                if not simulation_task:
                    simulation_task = asyncio.create_task(simulation.main())

        await asyncio.sleep(0.1)


simulation = Simulation()
asyncio.run(command_handler(simulation))
