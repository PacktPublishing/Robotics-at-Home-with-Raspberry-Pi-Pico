import time
import board
import pwmio

A1_PWM = pwmio.PWMOut(board.GP17)

A1_PWM.duty_cycle = 2**16-1
time.sleep(0.3)
A1_PWM.duty_cycle = 2**15
time.sleep(0.3)
A1_PWM.duty_cycle = 0
