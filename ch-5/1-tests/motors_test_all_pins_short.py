import time
import robot

robot.motor_A1.value = True
time.sleep(0.3)
robot.motor_A1.value = False
time.sleep(0.3)
robot.motor_A2.value = True
time.sleep(0.3)
robot.motor_A2.value = False
time.sleep(0.3)
robot.motor_B1.value = True
time.sleep(0.3)
robot.motor_B1.value = False
time.sleep(0.3)
robot.motor_B2.value = True
time.sleep(0.3)
robot.motor_B2.value = False
