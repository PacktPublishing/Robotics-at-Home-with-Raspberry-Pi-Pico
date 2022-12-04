import asyncio
import json
from guassian import get_gaussian_sample
from ulab import numpy as np

import arena
import robot


class Simulation:
    def __init__(self):
        self.population_size = 50
        self.left_distance = 100
        self.right_distance = 100

        # poses can be a list of x[pop size], y[pop size], heading[pop size]
        # while less "pythonic" it is more "numpyish"
        self.poses = np.empty((3, 0), dtype=np.float)
        self.regenerate_poses()
        self.mean = np.array((arena.width / 2, arena.height / 2, 180), dtype=np.float)
        self.std = np.array((arena.width / 4, arena.height / 4, 180), dtype=np.float)

    def regenerate_poses(self):
        # determine the number
        number_to_make = self.population_size - len(self.poses[0])
        new_poses = np.empty((3, number_to_make), dtype=np.float)
        # determine the mean and std for new poses
        if len(self.poses[0]) > 0:
            self.mean = np.mean(self.poses, 0)
            self.std = np.std(self.poses, 0)
        else:
            self.mean = np.array((arena.width / 2, arena.height / 2, 180))
            self.std = np.array((arena.width / 4, arena.height / 4, 180))
        print("mean.shape :", mean.shape)
        print("std.shape :", std.shape)

        # generate new poses
        print(f"Generating {number_to_make} new poses.")
        for n in range(number_to_make):
            new_poses[0, n] = get_gaussian_sample(self.mean[0], self.std[0])
            new_poses[1, n] = get_gaussian_sample(self.mean[1], self.std[1])
            new_poses[2, n] = get_gaussian_sample(self.mean[2], self.std[2])
        # set poses to concatenation of new poses and remaining poses
        self.poses = np.concatenate((self.poses, new_poses), axis=1)

    # hmm - cannot expand, or resize np arrays.
    # maybe we use normal py arrays apart from the mean/std bit?
    # a real numpy whizz may have a better way.
    
    

    async def move_robot(self):
        starting_heading = robot.imu.euler[0]
        encoder_left = robot.left_encoder.read()
        encoder_right = robot.right_encoder.read()
        robot.set_left(0.8)
        robot.set_right(0.8)
        await asyncio.sleep(0.1)
        # record sensor changes
        left_movement = robot.left_encoder.read() - encoder_left
        right_movement = robot.right_encoder.read() - encoder_right
        speed_in_mm = robot.ticks_to_m * ((left_movement + right_movement) / 2) * 1000
        new_heading = robot.imu.euler[0]
        if new_heading:
          heading_change = starting_heading - new_heading
        else:
          print("Failed to get heading")
          heading_change = 0

        # move poses
        radians = np.radians(self.poses[2])
        self.poses[0] += speed_in_mm * np.cos(radians)
        self.poses[1] += speed_in_mm * np.sin(radians)
        self.poses[2] += np.full(self.poses[2].shape, heading_change)
        self.poses[2] = np.vectorize(lambda n: n % 360)(self.poses[2])

    # ```
    # >>> first = np.array([[1, 2, 3, 4], [5,6,7,8]])
    # >>> second = np.array([3, 6, 9, 12])
    # >>> first + second
    # array([[ 4,  8, 12, 16],
    #        [ 8, 12, 16, 20]])
    # >>> second = np.array([[3, 6, 9, 12], [1,1,1,1]])
    # >>> first + second
    # array([[ 4,  8, 12, 16],
    #        [ 6,  7,  8,  9]])
    # >>> test=np.arange(10)
    # >>> test
    # array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], dtype=int16)
    # >>> mask = np.empty(len(test), dtype=np.bool)
    # >>> mask
    # array([False, False, False, False, False, False, False, False, False], dtype=bool)
    # >>> mask[3] = [True]
    # >>> mask[5] = [True]
    # >>> mask[6] = [True]
    # >>> test[mask]
    # array([4, 6, 7], dtype=int16)
    # ```

    def eliminate_poses(self, left_distance, right_distance):
        poses_to_keep = np.empty(len(self.poses[0]), dtype=np.bool)
        # first eliminate those outside the arena
        for position, pose in enumerate(self.poses.transpose()):
            # first those outside the arena
            poses_to_keep[position] = [arena.point_is_inside_arena(pose[0], pose[1])]
        # apply the keep as a mask to the poses using ulab.
        self.poses = np.array(
            [
                self.poses[0][poses_to_keep],
                self.poses[1][poses_to_keep],
                self.poses[2][poses_to_keep],
            ]
        )

        # Then deal with sensors
        # todo: would reorganising these pose arrays let us better use ulab tools?
        distance_sensors = np.empty((4, len(self.poses[0])), dtype=np.float)
        # sensors - they are facing forward, either side of the robot. Project them out to the sides
        distance_sensors[0] = self.poses[
            0
        ] + robot.distance_sensor_from_middle * np.cos(np.radians(self.poses[2] + 90))
        distance_sensors[1] = self.poses[
            1
        ] + robot.distance_sensor_from_middle * np.sin(np.radians(self.poses[2] + 90))
        # sensor right
        distance_sensors[2] = self.poses[
            0
        ] + robot.distance_sensor_from_middle * np.cos(np.radians(self.poses[2] - 90))
        distance_sensors[3] = self.poses[
            1
        ] + robot.distance_sensor_from_middle * np.sin(np.radians(self.poses[2] - 90))
        # now project these sensors forward based on their distance read
        distance_sensors[0] += np.cos(np.radians(self.poses[2])) * left_distance
        distance_sensors[1] += np.sin(np.radians(self.poses[2])) * left_distance
        distance_sensors[2] += np.cos(np.radians(self.poses[2])) * right_distance
        distance_sensors[3] += np.sin(np.radians(self.poses[2])) * right_distance
        # now eliminate those sensors that are too far outside the boundary
        # extension (extra layer) - those too far inside the boundary
        # extension (if needed) - make the boundary fuzzier - 20cm error?
        # poses to keep must be redefined - it's now shorter
        poses_to_keep = np.empty(len(self.poses[0]), dtype=np.bool)
        boundary_error = 100 # mm
        for position, distance_sensor in enumerate(distance_sensors.transpose()):
            poses_to_keep[position] = [
                arena.point_near_boundaries(distance_sensor[0], distance_sensor[1], boundary_error)
                and arena.point_near_boundaries(distance_sensor[2], distance_sensor[3], boundary_error)
            ]
        # apply the keep as a mask to the poses using ulab.
        self.poses = np.array(
            [
                self.poses[0][poses_to_keep],
                self.poses[1][poses_to_keep],
                self.poses[2][poses_to_keep],
            ]
        )
        print(self.poses.shape)

    # Helpful note - when debugging this numpy code, use prints with the serial console
    # printing the object shape is often a very helpful way to debug what is going on.
    # Eg:
    #    print("poses_to_keep.shape:", poses_to_keep.shape)
    #    print("self.poses[0].shape:", self.poses[0].shape)

    # steps:
    # regenerate poses
    # move robot
    # eliminate poses
    # send poses
    async def distance_sensor_updater(self):
        robot.left_distance.start_ranging()
        robot.right_distance.start_ranging()
        while True:
            if robot.left_distance.data_ready and robot.left_distance.distance:
                self.left_distance = robot.left_distance.distance * 10  # convert to mm
                robot.left_distance.clear_interrupt()
            if robot.right_distance.data_ready and robot.right_distance.distance:
                self.right_distance = robot.right_distance.distance * 10
                robot.right_distance.clear_interrupt()
            await asyncio.sleep(0.1)

    async def run(self):
        asyncio.create_task(self.distance_sensor_updater())
        try:
            for _ in range(15):
                self.regenerate_poses()
                await self.move_robot()
                self.eliminate_poses(self.left_distance, self.right_distance)
        finally:
            robot.stop()


def send_json(data):
    robot.uart.write((json.dumps(data) + "\n").encode())


def read_command():
    data = robot.uart.readline()
    try:
        decoded = data.decode()
    except UnicodeError:
        print("UnicodeError decoding :")
        print(data)
        return None
    try:
        request = json.loads(decoded)
    except ValueError:
        print("ValueError reading json from:")
        print(decoded)
        return None
    return request


async def updater(simulation):
    print("starting updater")
    while True:
        sys_status, gyro, accel, mag = robot.imu.calibration_status
        if sys_status < 3:
            send_json(
                {
                    "imu_calibration": {
                        "gyro": gyro,
                        "accel": accel,
                        "mag": mag,
                        "sys": sys_status,
                    }
                }
            )
        send_json(
            {
                "poses": simulation.poses.transpose().tolist(),
                "std": simulation.std.tolist(),
                "mean": simulation.mean.tolist(),
            }
        )
        await asyncio.sleep(0.5)


async def command_handler(simulation):
    update_task = asyncio.create_task(updater(simulation))
    print("Starting handler")
    simulation_task = None
    # This line - helpful to debug - rapid iteration on connected robot.
    # simulation_task = asyncio.create_task(simulation.run())
    while True:
        if robot.uart.in_waiting:
            print("Receiving data...")
            request = read_command()
            if not request:
                print("no request")
                continue
            # {"command": "arena"}
            if request["command"] == "arena":
                send_json(
                    {
                        "arena": arena.boundary_lines,
                        "target_zone": arena.target_zone,
                    }
                )
            elif request["command"] == "start":
                print("Starting simulation")
                if simulation_task is None or simulation_task.done():
                    simulation_task = asyncio.create_task(simulation.run())
            elif request["command"] == "stop":
                robot.stop()
                if simulation_task and not simulation_task.done():
                    simulation_task.cancel()
                    simulation_task = None
        await asyncio.sleep(0.1)


simulation = Simulation()
asyncio.run(command_handler(simulation))
