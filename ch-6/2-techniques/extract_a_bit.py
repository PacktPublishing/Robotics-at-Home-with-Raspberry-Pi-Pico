"""Sometimes we want to extract a specific bit for
comparison or testing"""
"""Shifting a register."""
import rp2pio
import adafruit_pioasm
import array

# extracting bit 2
bit_to_extract = 30
program = f"""
.program extract_bit
    pull block

; print initial state
    mov isr, osr
    push noblock    ; and use PUSH to put it on the receive FIFO

; extract - by shifting
    in osr, {bit_to_extract}  ; get n bits
    in null, 31  ; keep only 1 bit
    push noblock
"""

assembled = adafruit_pioasm.assemble(program)

## set up a statemachine
sm = rp2pio.StateMachine(
    assembled,
    frequency=2000,
)


buffer = array.array("I", [0])

sm.write(array.array("I", [0b01101000_00000000_00000000_00000000]))
# read the data
sm.readinto(buffer)
print("Initial Y: {0} 0b{0:032b} 0x{0:x}".format(buffer[0]))

sm.readinto(buffer)
print("Y bit extracted:  {0} 0b{0:032b} 0x{0:x}".format(buffer[0]))
