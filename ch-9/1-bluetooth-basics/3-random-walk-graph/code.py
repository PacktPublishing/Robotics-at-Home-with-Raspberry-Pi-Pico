import board 
from digitalio import DigitalInOut
import time
import busio
import supervisor
import random

led = DigitalInOut(board.LED)
led.switch_to_output()

# PICO UART pins? What am i not using?
uart = busio.UART(board.GP12,board.GP13,baudrate=9600, timeout=0.01)


def robot_data_source():
  sensor1 = random.randint(-100, 100)/100
  sensor2 = random.randint(-100, 100)/100
  while True:
      yield sensor1 * 100,sensor2 * 100
      sensor1 += random.randint(-100, 100)/1000
      sensor2 += random.randint(-100, 100)/800

data_source = robot_data_source()

print("Waiting for bytes on UART...")
while True:
    data = uart.read(32)
    if data is not None:
        print(data)
    # if our monotic time is a multiple of 50
    time.sleep(0.1)
    # 0.05 is too fast, 0.1 is about write - so 10 per second.
    sensor1, sensor2 = next(data_source)
    sensor_packet = f"{int(sensor1)},{int(sensor2)}\n"
    print(sensor_packet, end='')
    uart.write(sensor_packet.encode('utf-8'))
