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
    in null, 31         ; Clear ISR
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
left_enc = rp2pio.StateMachine(
    assembled, frequency=0, first_in_pin=board.GP20, in_pin_count=2
)

right_enc = rp2pio.StateMachine(
    assembled, frequency=0, first_in_pin=board.GP26, in_pin_count=2
)

buffer = array.array("I", [0])

left_data = 0
right_data = 0

while True:
    # read data from the fifo
    if left_enc.in_waiting:
        left_enc.readinto(buffer)
        left_data = buffer[0]
        # print it.
        print("{:08b}   {:08b}".format(left_data, right_data))
    if right_enc.in_waiting:
        right_enc.readinto(buffer)
        right_data = buffer[0]
        # print it.
        print("{:08b}   {:08b}".format(left_data, right_data))
