"""Shifting a register.
Default shift direction is in from the left.
Space is made for the new value, and n bits from the source are 
shifted in.
"""
import rp2pio
import adafruit_pioasm
import array


program = f"""
.program debug_register    
    set y, {0b10011}       ; set a value in y

; send it to be printed
    mov isr, y
    push noblock    ; and use PUSH to put it on the receive FIFO

; shift pts
    in null, 32     ; clear the isr
    in y,3         ; get n bits from y

    ; now send it to be printed
    push noblock    ; and use PUSH to put it on the receive FIFO

; show state of y
    mov isr, y
    push noblock
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
print("Before shift: {0} 0b{0:032b} 0x{0:x}".format(buffer[0]))

sm.readinto(buffer)
print("ISR shifted:  {0} 0b{0:032b} 0x{0:x}".format(buffer[0]))

sm.readinto(buffer)
print("Y state:      {0} 0b{0:032b} 0x{0:x}".format(buffer[0]))
