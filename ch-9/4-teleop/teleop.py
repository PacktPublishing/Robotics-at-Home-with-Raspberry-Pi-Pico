# .deploy/send-it.sh \
#   ch-9/4-teleop/sensor_remote.py \
#   ch-9/4-teleop/robot_wifi.py \
#   ch-9/4-teleop/robot.py \
#   ch-9/4-teleop/pio_encoder.py \
#   ch-9/4-teleop/sensor.html
import json
import time

from adafruit_esp32spi import adafruit_esp32spi_wsgiserver
from adafruit_wsgi.wsgi_app import WSGIApp

import robot_wifi
import robot

app = WSGIApp()

class State:
  stop_at = 0

state = State()

@app.route("/")
def index(request):
  with open("teleop.html") as fd:
    hello_html = fd.read()
  return 200, [('Content-Type',"text/html")], hello_html

@app.route("/move", methods=["POST"])
def movement(request):
  movement = json.loads(request.body)
  robot.set_left(movement['y'] + movement['x'])
  robot.set_right(movement['y'] - movement['x'])
  state.stop_at = time.time() + 1

print("Setting up wifi.")
wifi, esp = robot_wifi.connect_to_wifi()
server = adafruit_esp32spi_wsgiserver.WSGIServer(
  80,
  application=app 
)
adafruit_esp32spi_wsgiserver.set_interface(esp)

print("Starting server")

server.start()
ip_int = ".".join(str(int(n)) for n in esp.ip_address)
print(f"IP Address is {ip_int}")
while True:
    try:
        server.update_poll()
        # background task
        if state.stop_at < time.time():
          robot.stop()
    except:
        print("Shutting down wifi on failure. resetting ESP")
        wifi.reset()
        raise

# Reader exercise
# Can you combine the sensors and the control app? Can you think about how to control it using the sensors for feedback.
