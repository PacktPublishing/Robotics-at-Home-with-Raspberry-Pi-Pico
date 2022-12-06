import asyncio
import json
import random
from ulab import numpy as np
from guassian import get_gaussian_sample
import arena
import robot

# initial sample set - uniform
# then apply sensor model
# then resample
# then apply motion model
# and repeat

class Simulation:
    def __init__(self):
        self.population_size = 200
        self.left_distance = 100
        self.right_distance = 100
        # Poses - each an array of [x, y, heading]
        self.poses = np.array(
            [(random.uniform(0, arena.width), random.uniform(0, arena.height), random.uniform(0, 360)) for _ in range(self.population_size)],
            dtype=np.float,
        )
        self.distance_aim = 100

    def apply_sensor_model(self):
        # Based on vl53l1x sensor readings, create weight for each pose.
        # vl53l1x standard dev is +/- 5 mm. Each distance is a mean reading
        # we will first determine sensor positions based on poses
        # project forward based on distances sensed, introducing noise (based on standard dev)
        # then check this projected position against occupancy grid
        # and weight accordingly

        # distance sensor positions projected forward. left_x, left_y, right_x, right_y
        distance_sensor_positions = np.zeros(
            (self.poses.shape[0], 4), dtype=np.float)
        # sensors - they are facing forward, either side of the robot. Project them out to the sides
        # based on each poses heading
        # left sensor
        poses_left_90 = np.radians(self.poses[:, 2] + 90)
        # print("poses_left_90_shape:",poses_left_90.shape, "distance_sensor_positions_shape:",distance_sensor_positions.shape, "poses_shape:",self.poses.shape)
        distance_sensor_positions[:, 0] = self.poses[:, 0] + np.cos(poses_left_90) * robot.distance_sensor_from_middle
        distance_sensor_positions[:, 1] = self.poses[:, 1] + np.sin(poses_left_90) * robot.distance_sensor_from_middle
        # right sensor
        poses_right_90 = np.radians(self.poses[:, 2] - 90)
        distance_sensor_positions[:, 2] = self.poses[:, 0] + np.cos(poses_right_90) * robot.distance_sensor_from_middle
        distance_sensor_positions[:, 3] = self.poses[:, 1] + np.sin(poses_right_90) * robot.distance_sensor_from_middle
        # for each sensor position, find the distance to the nearest obstacle
        distance_sensor_standard_dev = 5
        dl_squared = self.left_distance ** 2
        dr_squared = self.right_distance ** 2

        # weighted poses a numpy array of weights for each pose
        weights = np.empty(self.poses.shape[0], dtype=np.float)

        for index, sensor_position in enumerate(distance_sensor_positions):
            # difference between this distance and the distance sensed is the error
            # add noise to this error
            if not arena.point_is_inside_arena(self.poses[index,0], self.poses[index,1]):
                weights[index] = 0
                continue
            # left sensor
            left_ray = sensor_position[0], sensor_position[1], np.radians(self.poses[index, 2])
            noise = get_gaussian_sample(0, distance_sensor_standard_dev)
            left_actual = arena.get_ray_distance_squared_to_nearest_boundary_segment(left_ray)
            if left_actual is None:
                print("left_actual is None. Ray was ", left_ray)
                left_actual = 100
            left_error = abs(left_actual - dl_squared + noise) # error
            # right sensor
            right_ray = sensor_position[2], sensor_position[3], np.radians(self.poses[index, 2])
            noise = get_gaussian_sample(0, distance_sensor_standard_dev)
            right_actual = arena.get_ray_distance_squared_to_nearest_boundary_segment(right_ray)
            if right_actual is None:
                print("right_actual is None. Ray was ", right_ray)
                right_actual = 100
            right_error = abs(right_actual - dr_squared + noise) #error
            # weight is the inverse of the error
            weights[index] = 1 / (left_error + right_error)

        #normalise the weights
        print("Weights sum before normalising:", np.sum(weights))
        weights = weights / np.sum(weights)
        print("Weights sum:", np.sum(weights))
        return weights

    def resample(self, weights):
        # based on the weights, resample the poses
        # weights is a numpy array of weights
        # resample is a numpy array of indices into the poses array
        samples = []
        # use low variance resampling
        start = random.uniform(0, 1 / self.population_size)
        cumulative_weights = weights[0]
        source_index = 0
        for current_index in range(self.population_size):
            sample_index = start + current_index / self.population_size
            while sample_index > cumulative_weights:
                source_index += 1
                cumulative_weights += weights[source_index]
            samples.append(source_index)
        # set poses to the resampled poses
        self.poses = np.array([self.poses[n] for n in samples])

    async def move_robot(self):
        """move forward, apply the motion model"""
        starting_heading = robot.imu.euler[0]
        encoder_left = robot.left_encoder.read()
        encoder_right = robot.right_encoder.read()

        # move forward - with collision avoidance
        print("left_distance:", self.left_distance, "right_distance:", self.right_distance)
        if min(self.left_distance, self.right_distance) < self.distance_aim:
            # we are too close to the wall
            # turn away from the wall
            # turn right if left distance is smaller
            # turn left if right distance is smaller
            forward_speed = 0
            if self.left_distance < self.right_distance:
                # turn right
                turn_speed = -0.5
            else:
                turn_speed = 0.5
        else:
            forward_speed = 0.8
        print("forward_speed:", forward_speed, "turn_speed:", turn_speed)
        robot.set_left(forward_speed + turn_speed)
        robot.set_right(forward_speed - turn_speed)

        await asyncio.sleep(0.05)
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

        # move poses (this is a bit cheeky, and should be using icc)
        heading_standard_dev = 2 # degrees
        speed_standard_dev = 5 # mm

        radians = np.radians(self.poses[:,2])
        heading_model = np.array([get_gaussian_sample(0, heading_standard_dev) for _ in range(self.poses.shape[0])])
        speed_model = np.array([get_gaussian_sample(speed_in_mm, speed_standard_dev) for _ in range(self.poses.shape[0])])
        self.poses[:,0] += speed_model * np.sin(radians)
        self.poses[:,1] += speed_model * np.cos(radians)
        self.poses[:,2] += heading_change + heading_model
        self.poses[:,2] = np.vectorize(lambda n: float(n % 360))(self.poses[:,2])

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
            await asyncio.sleep(0.01)

    async def run(self):
        asyncio.create_task(self.distance_sensor_updater())
        try:
            while True:
                # print("Applying sensor model")
                weights = self.apply_sensor_model()
                # print("Sensor model complete.\nResampling")
                self.resample(weights)
                # print("Resampling complete.\nMoving robot")
                await self.move_robot()
                # print("Robot move complete")
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
        # The big time delay is in sending the poses.
        print("Sending poses", simulation.poses.shape[0])
        for n in range(0, simulation.poses.shape[0], 10):
            # print("Sending poses from ", n, "to", n+10, "of", simulation.poses.shape[0], "poses")
            send_json({
                "poses": simulation.poses[n:n+10].tolist(),
                "offset": n,
            })
            await asyncio.sleep(0.01)
        await asyncio.sleep(0.5)


async def command_handler(simulation):
    print("Starting handler")
    update_task = None
    simulation_task = None
    while True:
        if robot.uart.in_waiting:
            print("Receiving data...")
            request = read_command()
            if not request:
                print("no request")
                continue
            if request["command"] == "arena":
                send_json(
                    {
                        "arena": arena.boundary_lines
                    }
                )
                if not update_task:
                    update_task = asyncio.create_task(updater(simulation))
            elif request["command"] == "start":
                simulation_task = asyncio.create_task(simulation.run())

        await asyncio.sleep(0.1)


simulation = Simulation()
asyncio.run(command_handler(simulation))
