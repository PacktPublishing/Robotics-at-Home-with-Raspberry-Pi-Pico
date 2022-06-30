import board 
import time
import busio
from adafruit_bluefruit_connect.accelerometer_packet import AccelerometerPacket
import robot


uart = busio.UART(board.GP12,board.GP13,baudrate=9600, timeout=0.01)

stop_at = 0
speed = 0.8

print("Waiting for accelerometer signals...")
while True:
  if uart.in_waiting:
    packet = AccelerometerPacket.from_stream(uart)
    speed = packet.z * 0.1
    turning = packet.y * 0.1
    if abs(speed) > 0.3 or abs(turning) > 0.1:
      print("speed:", speed, "turning:", turning)
      robot.set_left(speed + turning)
      robot.set_right(speed - turning)
    else:
      robot.stop()
    stop_at = time.time() + 1

  if time.time() > stop_at:
    robot.stop()
