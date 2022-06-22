import board 
import time
import busio
from adafruit_bluefruit_connect.button_packet import ButtonPacket
import robot


uart = busio.UART(board.GP12,board.GP13,baudrate=9600, timeout=0.01)

class RobotControl:
  stop_at = 0
  speed = 0.8
  timeout = 3

  def send_control(self, packet):
    if packet.button == ButtonPacket.UP:
      robot.set_left(self.speed)
      robot.set_right(self.speed)
    elif packet.button == ButtonPacket.DOWN:
      robot.set_left(-self.speed)
      robot.set_right(-self.speed)
    elif packet.button == ButtonPacket.LEFT:
      robot.set_left(-self.speed)
      robot.set_right(self.speed)
    elif packet.button == ButtonPacket.RIGHT:
      robot.set_left(self.speed)
      robot.set_right(-self.speed)
    self.stop_at = time.time() + self.timeout


control = RobotControl()

print("Waiting for control signals...")
while True:
    data = uart.read(32)
    if data is not None and data.startswith(b'!B'):
      packet = ButtonPacket.from_bytes(data)
      print("Button:", packet.button, "pressed:", packet.pressed)
      if packet.pressed:
        control.send_control(packet)
      else:
        robot.stop()

    if control.stop_at < time.time():
      robot.stop()        
