import board 
import time
import busio
from adafruit_bluefruit_connect.button_packet import ButtonPacket
import robot


uart = busio.UART(board.GP12,board.GP13,baudrate=9600, timeout=0.01)

stop_at = 0
speed = 0.8

print("Waiting for control signals...")
while True:
  if uart.in_waiting:
    packet = ButtonPacket.from_stream(uart)
    if packet:
      if not packet.pressed:
          robot.stop()
      elif packet.button == ButtonPacket.UP:
        robot.set_left(speed)
        robot.set_right(speed)
      elif packet.button == ButtonPacket.DOWN:
        robot.set_left(-speed)
        robot.set_right(-speed)
      elif packet.button == ButtonPacket.LEFT:
        robot.set_left(-speed)
        robot.set_right(speed)
      elif packet.button == ButtonPacket.RIGHT:
        robot.set_left(speed)
        robot.set_right(-speed)
      stop_at = time.time() + 3

  if time.time() > stop_at:
    robot.stop()
