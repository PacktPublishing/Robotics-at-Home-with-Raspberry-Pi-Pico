"""Send this code, run and watch the repl.
Then turn the wheel slowly to see the change"""
import time
import board
import rp2pio
import adafruit_pioasm
import array

pio_input = """
.program pio_input
    in pins, 1      ; read in pin (into ISR)
    push noblock    ; put this into input FIFO
"""

assembled = adafruit_pioasm.assemble(pio_input)

sm = rp2pio.StateMachine(
    assembled,
    frequency=2000,
    first_in_pin=board.GP20
)

buffer = array.array('I', [0])

while True:
    # read data from the fifo
    sm.readinto(buffer)
    # print it.
    print(f"{buffer[0]:032b}")
    time.sleep(0.1)
