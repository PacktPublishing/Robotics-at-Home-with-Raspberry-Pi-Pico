import asyncio
import json
import random
from ulab import numpy as np
import arena
import robot

class VaryingWallAvoid:
    def __init__(self):
        self.speed = 0.6

    def speed_from_distance(self, distance):
        limited_error = min(distance, 300) * self.speed
        motor_speed = limited_error / 300
        if motor_speed < 0.2:
            motor_speed = -0.3
        return motor_speed

    def update(self, left_distance, right_distance):
        left = self.speed_from_distance(left_distance)
        right = self.speed_from_distance(right_distance)
        robot.set_left(left)
        robot.set_right(right)

triangular_proportion = np.sqrt(6) / 2
def get_triangular_sample(mean, standard_deviation):
    base = triangular_proportion * (random.uniform(-standard_deviation, standard_deviation) + random.uniform(-standard_deviation, standard_deviation))
    return mean + base

class Simulation:
    def __init__(self):
        self.population_size = 100
        self.left_distance = 100
        self.right_distance = 100
        self.imu_mix = 0.3 * 0.5
        self.encoder_mix = 0.7
        self.rotation_standard_dev = 2 # degrees
        self.speed_standard_dev = 5 # mm

        # Poses - each an array of [x, y, heading]
        self.poses = np.array(
            [(
                int(random.uniform(0, arena.width)),
                int(random.uniform(0, arena.height)),
                int(random.uniform(0, 360))) for _ in range(self.population_size)],
            dtype=np.int16,
        )
        self.collision_avoider = VaryingWallAvoid()

    async def apply_sensor_model(self):
        # Based on vl53l1x sensor readings, create weight for each pose.
        # vl53l1x standard dev is +/- 5 mm. Each distance is a mean reading
        # we will first determine sensor positions based on poses
        # project forward based on distances sensed, introducing noise (based on standard dev)
        # then check this projected position against occupancy grid
        # and weight accordingly

        # distance sensor positions projected forward. x, y
        distance_sensor_left = np.zeros(
            (self.poses.shape[0], 2), dtype=np.float)
        distance_sensor_right = np.zeros(
            (self.poses.shape[0], 2), dtype=np.float)
        # sensors - they are facing forward, either side of the robot. Project them out to the sides
        # based on each poses heading and turn sensors into rays,
        # left sensor
        poses_left_90 = np.radians(self.poses[:, 2] + 90)
        distance_sensor_left[:, 0] = self.poses[:, 0] + np.cos(poses_left_90) * robot.distance_sensor_from_middle
        distance_sensor_left[:, 1] = self.poses[:, 1] + np.sin(poses_left_90) * robot.distance_sensor_from_middle
        # now project forward by distance sensor range
        distance_sensor_left[:, 0] += np.cos(self.poses[:, 2]) * self.left_distance
        distance_sensor_left[:, 1] += np.sin(self.poses[:, 2]) * self.left_distance
        # right sensor
        poses_right_90 = np.radians(self.poses[:, 2] - 90)
        distance_sensor_right[:, 0] = self.poses[:, 0] + np.cos(poses_right_90) * robot.distance_sensor_from_middle
        distance_sensor_right[:, 1] = self.poses[:, 1] + np.sin(poses_right_90) * robot.distance_sensor_from_middle
        # now project forward by distance sensor range
        distance_sensor_right[:, 0] += np.cos(self.poses[:, 2]) * self.left_distance
        distance_sensor_right[:, 1] += np.sin(self.poses[:, 2]) * self.left_distance

        await asyncio.sleep(0)
        # weighted poses a numpy array of weights for each pose
        weights = np.empty(self.poses.shape[0], dtype=np.float)
        for index in range(self.poses.shape[0]):
            # remove any that are outside the arena
            if not arena.point_is_inside_arena(self.poses[index,0], self.poses[index,1]):
                weights[index] = 0
                continue
            # difference between this distance and the distance sensed is the error
            # weight is the inverse of the error
            weights[index] = arena.get_distance_grid_at_point(distance_sensor_left[index,0], distance_sensor_left[index,1])
            weights[index] += arena.get_distance_grid_at_point(distance_sensor_left[index,0], distance_sensor_left[index,1])
        await asyncio.sleep(0)
        #normalise the weights
        weights = weights / np.sum(weights)
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

    def convert_odometry_to_motion(self, left_encoder_delta, right_encoder_delta):
        # convert odometry to motion
        # left_encoder is the change in the left encoder
        # right_encoder is the change in the right encoder
        # returns rot1, trans, rot2 
        # rot1 is the rotation of the robot in radians before the translation
        # trans is the distance the robot has moved in mm
        # rot2 is the rotation of the robot in radians  

        # convert encoder counts to mm
        left_mm = left_encoder_delta * robot.ticks_to_mm
        right_mm = right_encoder_delta * robot.ticks_to_mm

        if left_mm == right_mm:
            # no rotation
            return 0, left_mm, 0

        # calculate the ICC
        radius = (robot.wheelbase_mm / 2) * (left_mm + right_mm) / (right_mm - left_mm)
        theta = (right_mm - left_mm) / robot.wheelbase_mm
        # For a small enough motion, assume that the chord length = arc length
        arc_length = theta * radius
        rot1 = np.degrees(theta/2)
        rot2 = rot1
        return rot1, arc_length, rot2

    async def motion_model(self):
        """move forward, apply the motion model"""
        starting_heading = robot.imu.euler[0]
        encoder_left = robot.left_encoder.read()
        encoder_right = robot.right_encoder.read()

        await asyncio.sleep(0.01)
        rot1, trans, rot2 = self.convert_odometry_to_motion(
            robot.left_encoder.read() - encoder_left, 
            robot.right_encoder.read() - encoder_right)

        try:
            new_heading = robot.imu.euler[0]
        except OSError:
            new_heading = None
        if new_heading:
            heading_change = starting_heading - new_heading
            # blend with the encoder heading changes
            rot1 = rot1 * self.encoder_mix + heading_change * self.imu_mix
            rot2 = rot2 * self.encoder_mix + heading_change * self.imu_mix
        else:
            print("Failed to get heading")
        rot1_model = np.array([get_triangular_sample(rot1, self.rotation_standard_dev) for _ in range(self.poses.shape[0])])
        trans_model = np.array([get_triangular_sample(trans, self.speed_standard_dev) for _ in range(self.poses.shape[0])])
        rot2_model = np.array([get_triangular_sample(rot2, self.rotation_standard_dev) for _ in range(self.poses.shape[0])])
        self.poses[:,2] += rot1_model
        rot1_radians = np.radians(self.poses[:,2])
        self.poses[:,0] += trans_model * np.sin(rot1_radians)
        self.poses[:,1] += trans_model * np.cos(rot1_radians)
        self.poses[:,2] += rot2_model
        self.poses[:,2] = np.vectorize(lambda n: float(n % 360))(self.poses[:,2])
        self.poses = np.array(self.poses, dtype=np.int16)

    async def distance_sensor_updater(self):
        robot.left_distance.distance_mode = 2
        robot.right_distance.distance_mode = 2
        robot.left_distance.timing_budget = 50
        robot.right_distance.timing_budget = 50
        robot.left_distance.start_ranging()
        robot.right_distance.start_ranging()
        while True:
            if robot.left_distance.data_ready and robot.left_distance.distance:
                self.left_distance = robot.left_distance.distance * 10  # convert to mm
                robot.left_distance.clear_interrupt()
            if robot.right_distance.data_ready and robot.right_distance.distance:
                self.right_distance = robot.right_distance.distance * 10
                robot.right_distance.clear_interrupt()
            self.collision_avoider.update(self.left_distance, self.right_distance)
            await asyncio.sleep(0.01)

    async def run(self):
        asyncio.create_task(self.distance_sensor_updater())
        try:
            while True:
                weights = await self.apply_sensor_model()
                self.resample(weights)
                await self.motion_model()
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
        for n in range(0, simulation.poses.shape[0], 10):
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
                if not simulation_task:
                    simulation_task = asyncio.create_task(simulation.run())

        await asyncio.sleep(0.1)


simulation = Simulation()
asyncio.run(command_handler(simulation))
