import board
import pwmio
import pio_encoder

motor_A1 = pwmio.PWMOut(board.GP17)
motor_A2 = pwmio.PWMOut(board.GP16)
motor_B1 = pwmio.PWMOut(board.GP18)
motor_B2 = pwmio.PWMOut(board.GP19)

right_motor = motor_A1, motor_A2
left_motor = motor_B1, motor_B2

right_encoder = pio_encoder.QuadratureEncoder(board.GP20, board.GP21, reversed=True)
left_encoder = pio_encoder.QuadratureEncoder(board.GP26, board.GP27)

def stop():
    motor_A1.duty_cycle = 0
    motor_A2.duty_cycle = 0
    motor_B1.duty_cycle = 0
    motor_B2.duty_cycle = 0

def set_speed(motor, speed):
    # Swap motor pins if we reverse the speed
    if speed < 0:
        direction = motor[1], motor[0]
        speed = -speed
    else:
        direction = motor
    speed = min(speed, 1) # limit to 1.0
    max_speed = 2**16-1


    direction[0].duty_cycle = int(max_speed * speed)
    direction[1].duty_cycle = 0

def set_left(speed):
    set_speed(left_motor, speed)

def set_right(speed):
    set_speed(right_motor, speed)
