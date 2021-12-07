import time
import robot

robot.motor_A1.value = True
robot.motor_B1.value = True
time.sleep(0.3)
robot.motor_A1.value = False
robot.motor_B1.value = False
