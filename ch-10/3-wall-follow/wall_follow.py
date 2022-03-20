import time
import json
import math

from adafruit_esp32spi import adafruit_esp32spi_wsgiserver
from adafruit_wsgi.wsgi_app import WSGIApp

import pid
import robot
import robot_wifi


class FollowWallApp:
  def __init__(self) -> None:    
    self.speed = 0.6
    self.max_deflection = 0.4
    self.follow_pid = pid.PID(0.1, 0.5, 0, 15)
    self.follow_pid.dead_zone = 0.6

    self.wifi = None
    self.server = None

    self.last_time = time.monotonic_ns()
    self.left_dist = 0
    self.pid_output = 0

  def setup_robot(self):
    robot.left_distance.distance_mode = 1

  def setup_wifi(self, app):
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

  def index(self, request):
    return 200, [('Content-Type', 'application/json')], [json.dumps(
      {
        "last_value": self.follow_pid.last_value,
        "pid_output": self.pid_output,
        "time": self.last_time
      }
    )]

  def movement_update(self):
    # do we have data
    if robot.left_distance.data_ready:
      self.left_dist = robot.left_distance.distance
      
      # calculate time delta
      new_time = time.monotonic_ns()
      time_delta = new_time - self.last_time
      self.last_time = new_time

      # get turn from pid
      self.pid_output = self.follow_pid.update(self.left_dist, time_delta)
      deflection = self.pid_output * self.max_deflection

      # make movements
      robot.set_left(self.speed - deflection)
      robot.set_right(self.speed + deflection)

      # reset and loop
      robot.left_distance.clear_interrupt()

  def main_loop(self):
    robot.left_distance.start_ranging()
    self.last_time = time.monotonic()
    while True:
      try:
        self.movement_update()
        self.server.update_poll()
      except RuntimeError as e:
        print(f"Server poll error: {type(e)}, {e}")
        robot.stop()
        print(f"Resetting ESP...")
        self.wifi.reset()
        print("Reset complete.")

  def start(self):
    app = WSGIApp()
    app.route("/")(self.index)
    print("Starting")
    try:
      self.setup_robot()
      self.setup_wifi(app)
      self.main_loop()
    finally:
      robot.stop()
      robot.left_distance.clear_interrupt()
      robot.left_distance.stop_ranging()

FollowWallApp().start()
