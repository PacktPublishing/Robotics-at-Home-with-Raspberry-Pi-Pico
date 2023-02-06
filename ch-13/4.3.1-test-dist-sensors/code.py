import time
import json
import robot
import asyncio

def send_json(data):
    robot.send_line(json.dumps(data))

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

async def distance_reporter(sensors: DistanceSensorTracker):
    while True:
        data = {
            "distance": {
                "left": sensors.left, 
                "right": sensors.right
            }
        }
        print(data)
        send_json(data)
        await asyncio.sleep(0.1)

distance_sensors = DistanceSensorTracker()
asyncio.create_task(distance_sensors.main())
asyncio.run(distance_reporter(distance_sensors))
