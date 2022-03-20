"""We can reverse the content of a register."""
import rp2pio
import adafruit_pioasm
import array


program = """
.program reverse_register    
    set y, 21       ; set a value in y

; send it to be printed
    mov isr, y
    push noblock    ; and use PUSH to put it on the receive FIFO

; reverse it
    mov isr, :: y      ; copy and reversed the register into the ISR
; print it
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
