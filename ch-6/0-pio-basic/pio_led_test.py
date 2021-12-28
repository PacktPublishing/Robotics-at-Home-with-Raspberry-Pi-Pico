import time
import board
import rp2pio
import adafruit_pioasm

led_flash = """
.program led_flash
    pull
    out pins, 1
"""

assembled = adafruit_pioasm.assemble(led_flash)

sm = rp2pio.StateMachine(
    assembled,
    frequency=2000,
    first_out_pin=board.LED,
)
print("real frequency", sm.frequency)

while True:
    sm.write(bytes((1,)))
    time.sleep(0.5)
    sm.write(bytes((0,)))
    time.sleep(0.5)
