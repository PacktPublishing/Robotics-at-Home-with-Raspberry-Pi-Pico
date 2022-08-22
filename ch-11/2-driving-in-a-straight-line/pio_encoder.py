import rp2pio
import adafruit_pioasm
import array
import asyncio


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


class QuadratureEncoder:
    def __init__(self, first_pin, second_pin, reversed=False):
        """Encoder with 2 pins. Must use sequential pins on the board"""
        self.sm = rp2pio.StateMachine(
            assembled,
            frequency=0,
            first_in_pin=first_pin,
            jmp_pin=second_pin,
            in_pin_count=2,
        )
        self.reversed = reversed
        self._buffer = array.array("i", [0])
        asyncio.create_task(self.poll_loop())

    async def poll_loop(self):
        while True:
            await asyncio.sleep(0)
            while self.sm.in_waiting:
                self.sm.readinto(self._buffer)

    def read(self):
        if self.reversed:
            return -self._buffer[0]
        else:
            return self._buffer[0]
