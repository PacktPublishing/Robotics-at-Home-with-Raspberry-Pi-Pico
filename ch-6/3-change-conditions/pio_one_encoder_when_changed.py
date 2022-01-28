"""Send this code, run and watch the repl.
Then turn the wheel slowly to see the change"""
import board
import rp2pio
import adafruit_pioasm
import array

program = """
.program pio_input    
    set y, 0            ; clear y
read:
    mov x, y            ; store old Y in x
    in null, 32         ; Clear ISR
    in pins, 2          ; read in two pins (into ISR)
    mov y, isr          ; store ISR in y
    jmp x!=y different  ; Jump if its different
    jmp read            ; otherwise loop back to read

different:
    push noblock        ; put ISR into input FIFO
    jmp read            ; loop back
"""

assembled = adafruit_pioasm.assemble(program)

## set up a statemachine
sm = rp2pio.StateMachine(
    assembled,
    frequency=20000,
    first_in_pin=board.GP20,
    in_pin_count=2
)

buffer = array.array('I', [0])

while True:
    sm.readinto(buffer)
    print("{:032b}".format(buffer[0]))
