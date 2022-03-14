import json
import time
from digitalio import DigitalInOut
import board

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
  return 200, [('Content-Type',"text/html")], [hello_html]

@app.route("/control", methods=["POST"])
def control(request):
  movement = json.load(request.body)
  print(f"Received movement: {movement}")

  robot.set_left(-movement[1] + movement[0])
  robot.set_right(-movement[1] - movement[0])
  state.stop_at = time.time() + 1
  return 200, [('Content-Type',"application/json")], ["true"]

print("Setting up wifi.")
status_led = DigitalInOut(board.LED)
status_led.switch_to_output()
status_led.value = False


wifi, esp = robot_wifi.connect_to_wifi()
server = adafruit_esp32spi_wsgiserver.WSGIServer(
  80,
  application=app 
)
adafruit_esp32spi_wsgiserver.set_interface(esp)

print("Starting server")

server.start()
ip_int = ".".join(str(int(n)) for n in esp.ip_address)

status_led.value = True

print(f"IP Address is {ip_int}")
while True:
    try:
        status_led.value = False
        server.update_poll()
        status_led.value = True
        # background task
        if state.stop_at < time.time():
          robot.stop()
    except RuntimeError as e:
      print(f"Server poll error: {type(e)}, {e}")
      robot.stop()
      print(f"Resetting ESP...")
      wifi.reset()
      print("Reset complete.")
    except:
      print("Shutting down wifi on failure. resetting ESP")
      robot.stop()
      wifi.reset()
      raise

# Reader exercise
# Can you combine the sensors and the control app? Can you think about how to control it using the sensors for feedback.
