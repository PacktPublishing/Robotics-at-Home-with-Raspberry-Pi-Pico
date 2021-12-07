import time
import robot

robot.motor_A1.value = True
robot.motor_B2.value = True
time.sleep(0.3)
robot.stop()
