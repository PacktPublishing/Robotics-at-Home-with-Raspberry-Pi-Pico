import asyncio
import json
import time

import pid_controller
import robot


class RpmSpeedController:
    def __init__(self, encoder, motor_fn):
        self.encoder = encoder
        self.motor_fn = motor_fn
        self.pid = pid_controller.PIDController(3, 0, 1)
        self.speed = 0
        self.reset()

    def reset(self):
        self.last_ticks = self.encoder.read()
        self.pwm = 0
        self.pid.reset()

    def update(self, dt):
        current_ticks = self.encoder.read()
        speed_in_ticks = (current_ticks - self.last_ticks) / dt
        self.last_ticks = current_ticks
        # calculate the error
        error = self.speed - speed_in_ticks
        # calculate the control signal
        control_signal = self.pid.calculate(error, dt)
        self.pwm += control_signal
        self.motor_fn(self.pwm)


class MotionControl:
    def __init__(self):
        self.left_speed_controller = RpmSpeedController(robot.left_encoder, robot.set_left)
        self.right_speed_controller = RpmSpeedController(robot.right_encoder, robot.set_right)
        

    def plan_motion(self, turn1, distance, turn2):
        """Plan a motion - based on making a turn,
        moving forward a distance, 
        and then making another turn."""

        pass
    
    def uodate(self, dt):
        self.left_speed_controller.update(dt)
        self.right_speed_controller.update(dt)


async def main_loop(dt):
    motion_control = MotionControl()
    while True:
        await asyncio.sleep(dt)
        current_time = time.monotonic()
        dt = current_time - last_time
        last_time = current_time
        motion_control.uodate(dt)


async def command_handler():
    main_loop = None
    motion_control = MotionControl()
    robot = robot.Robot()
    while True:
        command = json.loads(input())
        if command["command"] == "start":
            main_loop = asyncio.create_task(main_loop(0.2))
        elif command["command"] == "get_speed":
            print(json.dumps(robot.get_speed()))
        else:
            print("Unknown command")

asyncio.run(command_handler())
