import json

from adafruit_esp32spi import adafruit_esp32spi_wsgiserver
from adafruit_wsgi.wsgi_app import WSGIApp

import robot_wifi
import robot

app = WSGIApp()

@app.route("/")
def index(request):
  with open("sensor.html") as fd:
    hello_html = fd.read()
  return 200, [('Content-Type',"text/html")], [hello_html]

@app.route("/sensors")
def sensors(request):
  sensor_data = {
    "left_distance": robot.left_distance.distance,
  }
  robot.left_distance.clear_interrupt()

  return 200, [('Content-Type', 'application/json')], [json.dumps(sensor_data)]

print("Setting up wifi.")
wifi, esp = robot_wifi.connect_to_wifi()
server = adafruit_esp32spi_wsgiserver.WSGIServer(
  80,
  application=app 
)
adafruit_esp32spi_wsgiserver.set_interface(esp)

print("Initialising sensors")
robot.left_distance.distance_mode = 1
robot.left_distance.start_ranging()


print("Starting server")

server.start()
ip_int = ".".join(str(int(n)) for n in esp.ip_address)
print(f"IP Address is {ip_int}")
while True:
    try:
        try:
          server.update_poll()
        except RuntimeError as e:
          print(f"Server poll error: {type(e)}, {e}")
        # background task
    except:
        print("Shutting down wifi on failure. resetting ESP")
        wifi.reset()
        raise
# Reader exercise
# add the right distance to the distance sensor remote. Consider where to position the meter for this, how to return both sensors in 
# the sensors call. Don't forget to clear the interrupt to get new readings.
