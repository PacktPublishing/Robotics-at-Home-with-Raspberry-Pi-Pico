"""Count down"""
import rp2pio
import adafruit_pioasm
import array


program = """
.program counting_up    
    set y, 21       ; set a value in y
    ; now send it to be printed
    mov isr, y
    push noblock    ; and use PUSH to put it on the receive FIFO
    
    ; Add 1
    mov y, ~ y      ; invert it
    jmp y--, fake    ; subtract from it
fake:
    mov isr, ~ y

    push noblock    ; and use PUSH to put it on the receive FIFO
"""

assembled = adafruit_pioasm.assemble(program)

## set up a statemachine
sm = rp2pio.StateMachine(
    assembled,
    frequency=2000,
)

buffer = array.array('I', [0])

# read the data
sm.readinto(buffer)
print("Before {0} 0b{0:08b} 0x{0:x}".format(buffer[0]))

# read the data
sm.readinto(buffer)
print("After {0} 0b{0:08b} 0x{0:x}".format(buffer[0]))
