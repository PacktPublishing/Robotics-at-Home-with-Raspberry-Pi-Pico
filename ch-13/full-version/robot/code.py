import asyncio
import json
import random
from ulab import numpy as np
import arena
import robot
import math
import time

# initial sample set - uniform
# then apply sensor model
# then resample
# then apply motion model
# and repeat

class VaryingWallAvoid:
    def __init__(self):
        self.speed = 0.6
        self.last_call = time.monotonic()

    def speed_from_distance(self, distance):
        limited_error = min(distance, 300) * self.speed
        motor_speed = limited_error / 300
        if motor_speed < 0.2:
            motor_speed = -0.3
        return motor_speed

    def update(self, left_distance, right_distance):
        # Currently being called every 1.6 seconds - that is far too long.
        print("Since last call:", time.monotonic() - self.last_call)
        left = self.speed_from_distance(left_distance)
        right = self.speed_from_distance(right_distance)
        # print("left speed:", left, "right speed:", right)
        robot.set_left(left)
        robot.set_right(right)
        self.last_call = time.monotonic()

triangular_proportion = math.sqrt(6) / 2
def get_triangular_sample(mean, standard_deviation):
    base = triangular_proportion * (random.uniform(-standard_deviation, standard_deviation) + random.uniform(-standard_deviation, standard_deviation))
    return mean + base

class Simulation:
    def __init__(self):
        self.population_size = 50
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
        # Timing is about 0.65s
        # Based on vl53l1x sensor readings, create weight for each pose.
        # vl53l1x standard dev is +/- 5 mm. Each distance is a mean reading
        # we will first determine sensor positions based on poses
        # project forward based on distances sensed, introducing noise (based on standard dev)
        # then check this projected position against occupancy grid
        # and weight accordingly

        # distance sensor positions projected forward. x, y, heading, reading
        fn_start = time.monotonic()
        print("Starting apply sensor model")
        distance_sensor_left_rays = np.zeros(
            (self.poses.shape[0], 3), dtype=np.float)
        distance_sensor_right_rays = np.zeros(
            (self.poses.shape[0], 3), dtype=np.float)
        # sensors - they are facing forward, either side of the robot. Project them out to the sides
        # based on each poses heading and turn sensors into rays,
        # left sensor
        poses_left_90 = np.radians(self.poses[:, 2] + 90)
        # print("poses_left_90_shape:",poses_left_90.shape, "distance_sensor_positions_shape:",distance_sensor_positions.shape, "poses_shape:",self.poses.shape)
        distance_sensor_left_rays[:, 0] = self.poses[:, 0] + np.cos(poses_left_90) * robot.distance_sensor_from_middle
        distance_sensor_left_rays[:, 1] = self.poses[:, 1] + np.sin(poses_left_90) * robot.distance_sensor_from_middle
        distance_sensor_left_rays[:, 2] = np.radians(self.poses[:, 2])
        # right sensor
        poses_right_90 = np.radians(self.poses[:, 2] - 90)
        distance_sensor_right_rays[:, 0] = self.poses[:, 0] + np.cos(poses_right_90) * robot.distance_sensor_from_middle
        distance_sensor_right_rays[:, 1] = self.poses[:, 1] + np.sin(poses_right_90) * robot.distance_sensor_from_middle
        distance_sensor_right_rays[:, 2] = np.radians(self.poses[:, 2])
        # for each sensor position, find the distance to the nearest obstacle
        distance_sensor_standard_dev = 5
        dl_squared = self.left_distance ** 2
        dr_squared = self.right_distance ** 2
        await asyncio.sleep(0)
        print("Time to calculate sensor positions:", time.monotonic() - fn_start)
        fn_start = time.monotonic()
        # weighted poses a numpy array of weights for each pose
        weights = np.empty(self.poses.shape[0], dtype=np.float)
        # 0.6 seconds in this loop!
        for index in range(self.poses.shape[0]):
            # remove any that are outside the arena
            if not arena.point_is_inside_arena(self.poses[index,0], self.poses[index,1]) or \
                    not arena.point_is_inside_arena(distance_sensor_left_rays[index,0], distance_sensor_left_rays[index,1]) or \
                    not arena.point_is_inside_arena(distance_sensor_right_rays[index,0], distance_sensor_right_rays[index,1]):
                weights[index] = 0
                continue
            # difference between this distance and the distance sensed is the error
            # add noise to this error
            # left sensor
            noise = get_triangular_sample(0, distance_sensor_standard_dev)
            left_actual = arena.get_ray_distance_squared_to_nearest_boundary_segment(distance_sensor_left_rays[index])
            left_error = abs(left_actual - dl_squared + noise)
            # right sensor
            noise = get_triangular_sample(0, distance_sensor_standard_dev)
            right_actual = arena.get_ray_distance_squared_to_nearest_boundary_segment(distance_sensor_right_rays[index])
            right_error = abs(right_actual - dr_squared + noise)
            # weight is the inverse of the error
            weights[index] = 1 / (left_error + right_error)
        print("Time to calculate pose weights", time.monotonic() - fn_start)
        await asyncio.sleep(0)
        #normalise the weights
        # print("Weights sum before normalising:", np.sum(weights))
        weights = weights / np.sum(weights)
        # print("Weights sum:", np.sum(weights))
        return weights

    def resample(self, weights):
        # Fast - 0.01 to 0.035 seconds
        # based on the weights, resample the poses
        # weights is a numpy array of weights
        # resample is a numpy array of indices into the poses array
        # fn_start = time.monotonic()
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
        # print("resample time", time.monotonic() - fn_start)

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
        # fn_start = time.monotonic()
        # Reading sensors - 0.001 to 0.002 seconds.
        starting_heading = robot.imu.euler[0]
        encoder_left = robot.left_encoder.read()
        encoder_right = robot.right_encoder.read()
        # print("Reading sensors time", time.monotonic() - fn_start)

        await asyncio.sleep(0.01)
        # fn_start = time.monotonic()
        # record sensor changes - 0.001 to 0.002 seconds
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
        # print("Got headings time", time.monotonic() - fn_start)
        # fn_start = time.monotonic()
        # move poses 0.07 - 0.08 seconds
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
        # print("Move poses times", time.monotonic() - fn_start)

    async def distance_sensor_updater(self):
        robot.left_distance.distance_mode = 2
        robot.right_distance.distance_mode = 2
        robot.left_distance.timing_budget = 50
        robot.right_distance.timing_budget = 50
        robot.left_distance.start_ranging()
        robot.right_distance.start_ranging()
        while True:
            # About 0.02 seconds
            # loop_start = time.monotonic()
            if robot.left_distance.data_ready and robot.left_distance.distance:
                self.left_distance = robot.left_distance.distance * 10  # convert to mm
                robot.left_distance.clear_interrupt()
            if robot.right_distance.data_ready and robot.right_distance.distance:
                self.right_distance = robot.right_distance.distance * 10
                robot.right_distance.clear_interrupt()
            print("left_distance:", self.left_distance, "right_distance:", self.right_distance)
            # move forward - with collision avoidance 0.03 to 0.04 seconds
            self.collision_avoider.update(self.left_distance, self.right_distance)

            # print("distance_sensor_updater_used_time: ", time.monotonic() - loop_start)
            await asyncio.sleep(0.01)

    async def run(self):
        asyncio.create_task(self.distance_sensor_updater())
        try:
            while True:
                # print("Applying sensor model")
                weights = await self.apply_sensor_model()
                # print("Sensor model complete.\nResampling")
                self.resample(weights)
                # print("Resampling complete.\nMoving robot")
                await self.motion_model()
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
        loop_start = time.monotonic()
        # Imu calibration and send - 0.0625 seconds
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
        print("Sent imu calibration in", time.monotonic() - loop_start)
        # The big time delay is in sending the poses.
        print("Sending poses", simulation.poses.shape[0])
        for n in range(0, simulation.poses.shape[0], 10):
            loop_start = time.monotonic()
            # each pose group is 0.2 seconds.
            # print("Sending poses from ", n, "to", n+10, "of", simulation.poses.shape[0], "poses")
            send_json({
                "poses": simulation.poses[n:n+10].tolist(),
                "offset": n,
            })
            print("Sent poses in", time.monotonic() - loop_start)
            await asyncio.sleep(0.01)
        await asyncio.sleep(0.5)


async def command_handler(simulation):
    print("Starting handler")
    update_task = None
    simulation_task = None
    # simulation_task = asyncio.create_task(simulation.run())
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
