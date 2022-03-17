import time
import json
import math

from adafruit_esp32spi import adafruit_esp32spi_wsgiserver
from adafruit_wsgi.wsgi_app import WSGIApp

import pid
import robot
import robot_wifi


app = WSGIApp()

class FollowWallApp:
  def __init__(self) -> None:    
    self.    self.speed = 0.6
 = 0.6
    self.max_deflection = 0.4

    self.set_point = 15
    self.follow_pid = pid.PID(0.1, 0, 0)
    self.wifi = None
    self.server = None

    self.last_time = 0
    self.left_dist = 0
    self.error_value = 0
    self.pid_output = 0

  def setup_robot():
    robot.left_distance.distance_mode = 1

  def setup_wifi(self):
    print("Setting up wifi.")
    self.wifi, esp = robot_wifi.connect_to_wifi()
    self.server = adafruit_esp32spi_wsgiserver.WSGIServer(
      80,
      application=app 
    )
    adafruit_esp32spi_wsgiserver.set_interface(esp)
    print("Starting server")

    self.server.start()
    ip_int = ".".join(str(int(n)) for n in esp.ip_address)
    print(f"IP Address is {ip_int}")

  @app.route("/")
  def index(self, request):
    return 200, [('Content-Type', 'application/json')], [json.dumps(
      {
        "error_value": self.error_value,
        "left_dist": self.left_dist,
        "pid_output": self.pid_output,
        "last_time": self.last_time
      }
    )]      

  @app.route("/set_point")
  def set_point(self, request):
    return 200, [('Content-Type', 'application/json')], [json.dumps(self.set_point)]

  def movement_update(self):
    # do we have data
    if robot.left_distance.data_ready:
      self.left_dist = robot.left_distance.distance
      
      # get error value
      self.error_value = self.left_dist - self.set_point

      # calculate time delta
      new_time = time.monotonic()
      time_delta = new_time - self.last_time
      self.last_time = new_time

      # get turn from pid
      self.pid_output = self.follow_pid.update(self.error_value, time_delta)
      deflection = min(self.max_deflection, self.pid_output)
      deflection = max(-self.max_deflection, deflection)

      # make movements
      print(f"Dist: {self.left_dist}, Err: {self.error_value}, Deflection: {deflection}")
      robot.set_left(self.speed + deflection)
      robot.set_right(self.speed - deflection)

      # reset and loop
      robot.left_distance.clear_interrupt()

  def main_loop(self):
    robot.left_distance.start_ranging()
    self.last_time = time.monotonic()
    while True:
      try:
        self.movement_update()
        self.server.update_poll()
        time.sleep(0.1)
      except RuntimeError as e:
        print(f"Server poll error: {type(e)}, {e}")
        robot.stop()
        print(f"Resetting ESP...")
        self.wifi.reset()
        print("Reset complete.")

  def start(self):
    print("Starting")
    try:
      self.setup_robot()
      self.setup_wifi()
      self.main_loop()
    finally:
      robot.stop()
      robot.left_distance.clear_interrupt()
      robot.left_distance.stop_ranging()

FollowWallApp().start()
