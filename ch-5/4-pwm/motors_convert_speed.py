import time
import robot

max_speed = 2**16-1

robot.motor_A1.duty_cycle = int(0.8 * max_speed)
time.sleep(0.3)
robot.stop()