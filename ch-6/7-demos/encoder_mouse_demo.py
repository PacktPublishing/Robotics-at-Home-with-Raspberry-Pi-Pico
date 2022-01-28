"""Copy the adafruit_hid folder into CIRCUITPY, run this,
and move the wheels on the robot. Why? Why not."""
import robot
import usb_hid
from adafruit_hid.mouse import Mouse

print("Setting up Hid")
mouse = Mouse(usb_hid.devices)

last_x = 0
last_y = 0

print("Entering main loop")
while True:
  x = robot.left_encoder.read()
  y = robot.right_encoder.read()

  x_diff = x - last_x
  y_diff = y - last_y

  last_x = x
  last_y = y

  mouse.move(x=x_diff, y=y_diff)
