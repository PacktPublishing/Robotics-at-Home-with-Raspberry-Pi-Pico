"""Sometimes we want to extract a specific bit for
comparison or testing"""
"""Shifting a register."""
import rp2pio
import adafruit_pioasm
import array

def scenario(test_data, bit_to_extract, expected):
    program = f"""
    .program extract_bit    
        set y, {test_data}    ; set a value in y

    ; extract - by shifting
        in null, 32     ; clear the isr
        in y, {bit_to_extract + 1}         ; get n bits

; debug isr
        mov x, isr  ; preserve isr - pushing destroys it
        push noblock
        mov isr, x  ; restore isr
; done debug

        in null, 31  ; Shift off all but last bit (leaving it)

; debug isr        
        mov x, isr  ; preserve isr - pushing destroys it
        push noblock
        mov isr, x  ; restore isr
; done debug

        mov y, isr ; reverse the isr back into y

    ; send y to fifo
        mov isr, y
        push noblock    ; and use PUSH to put it on the receive FIFO
    """
    assembled = adafruit_pioasm.assemble(program)

    ## set up a statemachine
    with rp2pio.StateMachine(
        assembled,
        frequency=2000,
    ) as sm:
        buffer = array.array('I', [0])

        print("source bits: {0} 0b{0:032b} 0x{0:x}".format(test_data))
        sm.readinto(buffer)
        print("isr mid: {0} 0b{0:032b} 0x{0:x}".format(buffer[0]))
        sm.readinto(buffer)
        print("isr after shift off: {0} 0b{0:032b} 0x{0:x}".format(buffer[0]))
        sm.readinto(buffer)
        print("Y bit extracted:  {0} 0b{0:032b} 0x{0:x}".format(buffer[0]))
        if buffer[0] != expected:
            print("Didn't get what I expected")
            print("Y bit expected:  {0} 0b{0:032b} 0x{0:x}".format(expected))
        print("")

def pull_scenario(test_data, bit_to_extract, expected):
    program = f"""
    .program extract_bit_pull    
        pull   block    ; pull data
        mov y, osr      

    ; extract - by shifting
        in null, 32     ; clear the isr
        in y, {bit_to_extract + 1}         ; get n bits

; debug isr
        mov x, isr  ; preserve isr - pushing destroys it
        push noblock
        mov isr, x  ; restore isr
; done debug

        in null, 31  ; Shift off all but last bit (leaving it)

; debug isr        
        mov x, isr  ; preserve isr - pushing destroys it
        push noblock
        mov isr, x  ; restore isr
; done debug

        mov y, isr ; reverse the isr back into y

    ; send y to fifo
        mov isr, y
        push noblock    ; and use PUSH to put it on the receive FIFO
    """
    assembled = adafruit_pioasm.assemble(program)

    ## set up a statemachine
    with rp2pio.StateMachine(
        assembled,
        frequency=2000,
    ) as sm:
        sm.write(array.array('I', [test_data]))
        buffer = array.array('I', [0])

        print("source bits: {0} 0b{0:032b} 0x{0:x}".format(test_data))
        sm.readinto(buffer)
        print("isr mid: {0} 0b{0:032b} 0x{0:x}".format(buffer[0]))
        sm.readinto(buffer)
        print("isr after shift off: {0} 0b{0:032b} 0x{0:x}".format(buffer[0]))
        sm.readinto(buffer)
        print("Y bit extracted:  {0} 0b{0:032b} 0x{0:x}".format(buffer[0]))
        if buffer[0] != expected:
            print("Didn't get what I expected")
            print("Y bit expected:  {0} 0b{0:032b} 0x{0:x}".format(expected))
        print("")    

scenario(0b101, 1, 0)
scenario(0b110, 1, 1)
scenario(0b010, 1, 1)
scenario(0b100, 2, 1)
scenario(0b011, 2, 0)
scenario(0b1011, 3, 1)
scenario(0b1010, 3, 1)
scenario(0b1000, 3, 1)
scenario(0b0111, 3, 0)
# bit I want
#                 v
pull_scenario(0b10101000_00000000_00000000_00000000, 29, 1)
pull_scenario(0b11011000_00000000_00000000_00000000, 29, 0)
#                v
pull_scenario(0b01011000_00000000_00000000_00000000, 30, 1)
pull_scenario(0b10111000_00000000_00000000_00000000, 30, 0)
#               v
pull_scenario(0b10111000_00000000_00000000_00000000, 31, 1)
pull_scenario(0b01111000_00000000_00000000_00000000, 31, 0)

