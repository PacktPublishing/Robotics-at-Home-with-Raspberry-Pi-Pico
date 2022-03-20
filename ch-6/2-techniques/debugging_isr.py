"""Sometimes, you need to debug a register. 
ISR is a bit special - when you push, you destroy it's content -
    you'll need to restore this. If you remove the mov from x, 
    it is set to 0s.
It'll cost a few instructions to do."""
import rp2pio
import adafruit_pioasm
import array


program = """
.program debug_register    
    set y, 21       ; use y to set ISR
    mov isr, y

; debug isr
        mov x, isr  ; preserve isr - pushing destroys it
        push noblock
        mov isr, x  ; restore isr
; done debug

; debug isr
        mov x, isr  ; preserve isr - pushing destroys it
        push noblock
        mov isr, x  ; restore isr
; done debug
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
print("first push: {0} 0b{0:08b} 0x{0:x}".format(buffer[0]))

sm.readinto(buffer)
print("second:     {0} 0b{0:08b} 0x{0:x}".format(buffer[0]))
