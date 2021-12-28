"""Send this code, run and watch the repl.
Then turn the wheel slowly to see the change"""
import board
import rp2pio
import adafruit_pioasm

pio_input = """
.program pio_input    
    set y, 0            ; clear y
read:
    mov x, y            ; store old Y in x
    in null, 31         ; Clear ISR
    in pins, 2          ; read in two pins (into ISR)
    mov y, isr          ; store ISR in y
    jmp x!=y different  ; Jump if its different
    jmp read            ; otherwise loop back to read

different:
    push noblock        ; put ISR into input FIFO
    jmp read            ; loop back
"""

assembled = adafruit_pioasm.assemble(pio_input)

## set up a statemachine
sm = rp2pio.StateMachine(
    assembled,
    frequency=2000,
    first_in_pin=board.GP20,
    in_pin_count=2
)

buffer = bytearray(1) # an array of bytes to read into - we are just asking for a byte (are we though? It might be 4 bytes)

while True:
    # read data from the fifo
    # print (sm.in_waiting)
    if sm.in_waiting:
        data = sm.readinto(buffer)
        # print it.
        print("{:08b}".format(buffer[0]))
