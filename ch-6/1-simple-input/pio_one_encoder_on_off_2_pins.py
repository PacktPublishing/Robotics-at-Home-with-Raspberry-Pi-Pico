"""Send this code, run and watch the repl.
Then turn the wheel slowly to see the change"""
import board
import rp2pio
import adafruit_pioasm
import time

pio_input = """
.program pio_input
    in pins, 2      ; read in two pins (into ISR)
    push noblock    ; put ISR into input FIFO
"""

assembled = adafruit_pioasm.assemble(pio_input)

## set up a statemachine
sm = rp2pio.StateMachine(
    assembled,
    frequency=2000,
    first_in_pin=board.GP20,
    in_pin_count=2
)

buffer = bytearray(1) # an array of bytes to read into - we are just asking for a byte

while True:
    # read data from the fifo
    data = sm.readinto(buffer)
    # print it.
    print("{:08b}".format(buffer[0]))
