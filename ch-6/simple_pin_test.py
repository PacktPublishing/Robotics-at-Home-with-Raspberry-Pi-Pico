import time
import board
import digitalio

pin = digitalio.DigitalInOut(board.GP4)
pin.direction = digitalio.Direction.OUTPUT

while True:
    pin.value = True
    time.sleep(0.01)
    pin.value = False
    time.sleep(0.01)
