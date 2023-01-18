"""Send this code, run and watch the repl.
Then turn the wheel slowly to see the change"""
import board
import rp2pio
import adafruit_pioasm
import array

program = """
; use the osr for count
; input pins c1 c2

    set y, 0            ; clear y
    mov osr, y          ; and clear osr
read:
    ; x will be the old value
    ; y the new values
    mov x, y            ; store old Y in x
    in null, 32         ; Clear ISR - using y
    in pins, 2          ; read two pins into y
    mov y, isr
    jmp x!=y, different ; Jump if its different
    jmp read            ; otherwise loop back to read

different:
    ; x has old value, y has new.
    ; extract the upper bit of X.
    in x, 31             ; get bit 31 - old p1 (remember which direction it came in)
    in null, 31         ; keep only 1 bit
    mov x, isr          ; put this back in x
    jmp !x, c1_old_zero

c1_old_not_zero:
    jmp pin, count_up
    jmp count_down

c1_old_zero:
    jmp pin, count_down
    ; fall through
count_up:
    ; for a clockwise move - we'll add 1 by inverting
    mov x, ~ osr        ; store inverted OSR on x
    jmp x--, fake       ; use jump to take off 1
fake:
    mov x, ~ x          ; invert back
    jmp send
count_down:
    ; for a clockwise move, just take one off
    mov x, osr          ; store osr in x
    jmp x--, send       ; dec and send
send:
    ; send x.
    mov isr, x          ; send it
    push noblock        ; put ISR into input FIFO
    mov osr, x          ; put X back in OSR
    jmp read            ; loop back
"""

assembled = adafruit_pioasm.assemble(program)

## set up a statemachine
left_enc = rp2pio.StateMachine(
    assembled, frequency=0, first_in_pin=board.GP20, jmp_pin=board.GP21, in_pin_count=2
)

right_enc = rp2pio.StateMachine(
    assembled, frequency=0, first_in_pin=board.GP26, jmp_pin=board.GP27, in_pin_count=2
)

buffer = array.array("i", [0])

left_data = 0
right_data = 0

while True:
    # read data from the fifo
    if left_enc.in_waiting:
        left_enc.readinto(buffer)
        left_data = buffer[0]
        # print it.
        print(left_data, right_data)
    if right_enc.in_waiting:
        right_enc.readinto(buffer)
        right_data = buffer[0]
        # print it.
        print(left_data, right_data)
