import robot_wifi

from adafruit_esp32spi import adafruit_esp32spi_wsgiserver
from adafruit_wsgi.wsgi_app import WSGIApp

app = WSGIApp()

@app.route("/")
def index(request):
  with open("hello.html") as fd:
    hello_html = fd.read()
  return 200, [('Content-Type',"text/html")], hello_html

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
    except:
        print("Shutting down wifi on failure. resetting ESP")
        wifi.reset()
        raise
