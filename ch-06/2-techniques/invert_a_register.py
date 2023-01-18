"""We can invert the bits of a register."""
import rp2pio
import adafruit_pioasm
import array


program = """
.program invert_register    
    set y, 21       ; set a value in y

; send it to be printed
    mov isr, y
    push noblock    ; and use PUSH to put it on the receive FIFO
    
; invert
    mov isr, ~ y      ; copy and reversed the registe into the ISR
    ; send it to be printed
    push noblock    ; and use PUSH to put it on the receive FIFO
"""

assembled = adafruit_pioasm.assemble(program)

## set up a statemachine
sm = rp2pio.StateMachine(
    assembled,
    frequency=2000,
)

buffer = array.array("i", [0])

# read the data
sm.readinto(buffer)
print("{0} 0b{0:032b} 0x{0:x}".format(buffer[0]))

# read the data
sm.readinto(buffer)
print("{0} 0b{0:032b} 0x{0:x}".format(buffer[0]))
