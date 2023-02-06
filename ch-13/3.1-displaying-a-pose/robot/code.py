import asyncio
import json
import random
from ulab import numpy as np

import arena
import robot

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



async def command_handler(simulation):
    print("Starting handler")
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
                send_poses(simulation.poses)

        await asyncio.sleep(0.1)


simulation = Simulation()
asyncio.run(command_handler(simulation))
