import asyncio
import json
import random
from ulab import numpy as np

import arena
import robot
import traceback

from performance_counter import PerformanceCounter

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
        try:
            while True:
                robot.set_right(self.speed)
                while self.distance_sensors.left < 300 or \
                        self.distance_sensors.right < 300:
                    robot.set_left(-self.speed)
                    await asyncio.sleep(0.3)
                robot.set_left(self.speed)
                await asyncio.sleep(0)
        except Exception as e:
            send_json({"exception": traceback.format_exception(e, e, e.__traceback__)})
            raise
            
def get_random_sample(mean, scale):
    return mean + (random.uniform(-scale, scale) + random.uniform(-scale, scale)) / 2

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
    print(f"sending {len(samples)} poses")
    send_json({
        "poses": np.array(samples[:,:2], dtype=np.int16).tolist(),
    })


class Simulation:
    def __init__(self):
        self.population_size = 200
        self.poses = np.array(
            [(
                int(random.uniform(0, arena.width)),
                int(random.uniform(0, arena.height)),
                int(random.uniform(0, 360))) for _ in range(self.population_size)],
            dtype=np.float,
        )
        self.distance_sensors = DistanceSensorTracker()
        self.collision_avoider = CollisionAvoid(self.distance_sensors)
        self.last_encoder_left = robot.left_encoder.read()
        self.last_encoder_right = robot.right_encoder.read()
        self.alpha_rot = 0.05
        self.alpha_rot_trans = 0.01
        self.alpha_trans = 0.05
        self.alpha_trans_rot = 0.01
        
        # profiling
        self.pc_resample = PerformanceCounter()
        self.pc_odometry = PerformanceCounter()
        self.pc_move_poses = PerformanceCounter() # superset of odometry time
        self.pc_randomise_motion = PerformanceCounter()
        self.pc_motion_model = PerformanceCounter()
        self.pc_observe_distance_sensors = PerformanceCounter()
        self.pc_observation_model = PerformanceCounter()

    def resample(self, weights, sample_count):
        """Return sample_count number of samples from the
        poses, based on the weights array.
        Uses low variance resampling"""
        self.pc_resample.start()
        samples = np.zeros((sample_count, 3))
        interval = 1 / sample_count
        shift = random.uniform(0, interval)
        cumulative_weights = weights[0]
        source_index = 0
        for current_index in range(sample_count):
            weight_index = shift + current_index * interval
            while weight_index >= cumulative_weights:
                source_index += 1
                source_index = min(len(weights), source_index)
                cumulative_weights += weights[source_index]
            samples[current_index] = self.poses[source_index]
        self.pc_resample.stop()
        return samples

    def convert_odometry_to_motion(self, left_encoder_delta, right_encoder_delta):
        """
        left_encoder is the change in the left encoder
        right_encoder is the change in the right encoder
        returns rot1, trans, rot2 
        rot1 is the rotation of the robot in degrees before the translation
        trans is the distance the robot has moved in mm
        rot2 is the rotation of the robot in degrees
        """
        self.pc_odometry.start()
        left_mm = left_encoder_delta * robot.ticks_to_mm
        right_mm = right_encoder_delta * robot.ticks_to_mm

        if left_mm == right_mm:
            return 0, left_mm, 0

        # calculate the radius of the arc
        radius = (robot.wheelbase_mm / 2) * (left_mm + right_mm) / (right_mm - left_mm)
        ## angle = difference in steps / wheelbase
        d_theta = (right_mm - left_mm) / robot.wheelbase_mm
        # For a small enough motion, assume that the chord length = arc length
        arc_length = d_theta * radius
        rot1 = np.degrees(d_theta/2)
        rot2 = rot1
        self.pc_odometry.stop()
        return rot1, arc_length, rot2

    def move_poses(self, rot1, trans, rot2):
        self.pc_move_poses.start()
        self.poses[:,2] += rot1
        rot1_radians = np.radians(self.poses[:,2])
        self.poses[:,0] += trans * np.cos(rot1_radians)
        self.poses[:,1] += trans * np.sin(rot1_radians)
        self.poses[:,2] += rot2
        self.poses[:,2] = np.array([float(theta % 360) for theta in self.poses[:,2]])
        self.pc_move_poses.stop()

    def randomise_motion(self, rot1, trans, rot2):
        self.pc_randomise_motion.start()
        rot1_scale = self.alpha_rot * abs(rot1) + self.alpha_rot_trans * abs(trans)
        trans_scale = self.alpha_trans * abs(trans) + self.alpha_trans_rot * (abs(rot1) + abs(rot2))
        rot2_scale = self.alpha_rot * abs(rot2) + self.alpha_rot_trans * abs(trans)
        rot1_model = np.array([get_random_sample(rot1, rot1_scale) for _ in range(self.poses.shape[0])])
        trans_model = np.array([get_random_sample(trans, trans_scale) for _ in range(self.poses.shape[0])])
        rot2_model = np.array([get_random_sample(rot2, rot2_scale) for _ in range(self.poses.shape[0])])
        self.pc_randomise_motion.stop()
        return rot1_model, trans_model, rot2_model

    def motion_model(self):
        """Apply the motion model"""
        self.pc_motion_model.start()
        new_encoder_left = robot.left_encoder.read()
        new_encoder_right = robot.right_encoder.read()

        rot1, trans, rot2 = self.convert_odometry_to_motion(
            new_encoder_left - self.last_encoder_left, 
            new_encoder_right - self.last_encoder_right)
        self.last_encoder_left = new_encoder_left
        self.last_encoder_right = new_encoder_right

        rot1_model, trans_model, rot2_model = self.randomise_motion(rot1, trans, rot2)
        self.move_poses(rot1_model, trans_model, rot2_model)
# 
#         print(
#             json.dumps(
#                 [self.poses.tolist(), rot1, trans, rot2]
#             )
#         )
        self.pc_motion_model.stop()

    def observe_distance_sensors(self, weights):
        self.pc_observe_distance_sensors.start()
        # Sensor triangle left
        opposite = self.distance_sensors.left + robot.dist_forward_mm
        adjacent = robot.dist_side_mm
        left_angle = np.atan(opposite / adjacent)
        left_hypotenuse = np.sqrt(opposite**2 + adjacent**2)
        # Sensor triangle right
        opposite = self.distance_sensors.right + robot.dist_forward_mm
        adjacent = robot.dist_side_mm
        right_angle = np.atan(opposite / adjacent)
        right_hypotenuse = np.sqrt(opposite**2 + adjacent**2)

        # modify the current weights based on the distance sensors
        left_sensor = np.zeros((self.poses.shape[0], 2), dtype=np.float)
        right_sensor = np.zeros((self.poses.shape[0], 2), dtype=np.float)
        # left sensor
        poses_left_angle = np.radians(self.poses[:, 2]) + left_angle
        left_sensor[:, 0] = self.poses[:, 0] + np.cos(poses_left_angle) * left_hypotenuse
        left_sensor[:, 1] = self.poses[:, 1] + np.sin(poses_left_angle) * left_hypotenuse

        # right sensor
        poses_right_angle = np.radians(self.poses[:, 2]) - right_angle
        right_sensor[:, 0] = self.poses[:, 0] + np.cos(poses_right_angle) * right_hypotenuse
        right_sensor[:, 1] = self.poses[:, 1] + np.sin(poses_right_angle) * right_hypotenuse

        # Look up the distance in the arena
        for index in range(self.poses.shape[0]):
            sensor_weight = arena.get_distance_grid_at_point(left_sensor[index,0], left_sensor[index,1])
            sensor_weight += arena.get_distance_grid_at_point(right_sensor[index,0], right_sensor[index,1])
            weights[index] *= sensor_weight
        self.pc_observe_distance_sensors.stop()
        return weights

    def observation_model(self):
        self.pc_observation_model.start()
        weights = np.ones(self.poses.shape[0], dtype=np.float)
        for index, pose in enumerate(self.poses):
            if not arena.contains(pose[:1], pose[:2]):
                weights[index] = 0.01
        weights = self.observe_distance_sensors(weights)
        weights = weights / np.sum(weights)
        self.pc_observation_model.stop()
        return weights

    def print_pc_lines(self):
        if self.pc_odometry.count % 10 != 0:
            return
        
        print("Resample: ", self.pc_resample.performance_line())
        print("Odometry: ", self.pc_odometry.performance_line())
        print("Move Poses: ", self.pc_move_poses.performance_line())
        print("Randomise Motion: ", self.pc_randomise_motion.performance_line())
        print("Motion Model: ", self.pc_motion_model.performance_line())
        print("Observe Distance Sensors: ", self.pc_observe_distance_sensors.performance_line())
        print("Observation Model: ", self.pc_observation_model.performance_line())

    async def main(self):
        asyncio.create_task(self.distance_sensors.main())
        collision_avoider = asyncio.create_task(self.collision_avoider.main())
        try:
            while True:
                weights = self.observation_model()
                print("Weights: ", weights)
                send_poses(self.resample(weights, 20))
                self.poses = self.resample(weights, self.population_size)
                await asyncio.sleep(0.05)
                self.motion_model()
                self.print_pc_lines()
        except Exception as e:
            send_json({"exception": traceback.format_exception(e, e, e.__traceback__)})
            raise
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
