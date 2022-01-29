"""Sometimes, you need to debug a register. 
Note - ISR content is destroyed.
It'll cost a few instructions to do."""
import rp2pio
import adafruit_pioasm
import array


program = """
.program debug_register    
    set y, 21       ; set a value in y
    ; now send it to be printed
    mov isr, y      ; copy the register you need to dump into the ISR
    push noblock    ; and use PUSH to put it on the receive FIFO
"""

assembled = adafruit_pioasm.assemble(program)

## set up a statemachine
sm = rp2pio.StateMachine(assembled, frequency=2000)

buffer = array.array('I', [0])

# read the data
sm.readinto(buffer)
print("{0} 0b{0:032b}".format(buffer[0]))
