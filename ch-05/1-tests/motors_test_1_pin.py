import time
import board
import digitalio

motor_A1 = digitalio.DigitalInOut(board.GP18)
motor_A1.direction = digitalio.Direction.OUTPUT

motor_A1.value = True
time.sleep(0.3)
motor_A1.value = False
