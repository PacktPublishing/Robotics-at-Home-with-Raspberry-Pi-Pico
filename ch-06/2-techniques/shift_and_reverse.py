"""Shift and reverse"""
import rp2pio
import adafruit_pioasm
import array


program = """
.program debug_register    
    set y, 2       ; set a value in y


; send it to be printed
    mov isr, y
    push noblock    ; and use PUSH to put it on the receive FIFO

; shift and reverse
    in y, 1         ; get bits
    mov isr, :: isr ; reverse it

; print again
    push noblock    ; and use PUSH to put it on the receive FIFO
"""

assembled = adafruit_pioasm.assemble(program)

## set up a statemachine
sm = rp2pio.StateMachine(
    assembled,
    frequency=2000,
)

buffer = array.array("I", [0])

# read the data
sm.readinto(buffer)
print("{0} 0b{0:032b} 0x{0:x}".format(buffer[0]))

# read the data
sm.readinto(buffer)
print("{0} 0b{0:032b} 0x{0:x}".format(buffer[0]))
