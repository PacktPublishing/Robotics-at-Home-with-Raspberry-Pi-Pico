import time
import robot

robot.motor_A2.value = True
robot.motor_B2.value = True
time.sleep(0.3)
robot.motor_A2.value = False
robot.motor_B2.value = False
