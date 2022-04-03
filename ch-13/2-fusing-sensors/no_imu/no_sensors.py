import time
import json
import traceback

from adafruit_esp32spi import adafruit_esp32spi_wsgiserver
from adafruit_wsgi.wsgi_app import WSGIApp

import robot_wifi
import random


class RandomWalkSensors:
    def __init__(self):
        self.wifi = None
        self.server = None
        self.last_value = 0

        self.start_time = time.monotonic()
        self.last_time = self.start_time
        # self.app = None

    def setup_wifi(self, app):
        # self.app = app
        print("Setting up wifi.")
        self.wifi, esp = robot_wifi.connect_to_wifi()
        self.server = adafruit_esp32spi_wsgiserver.WSGIServer(80, application=app)
        adafruit_esp32spi_wsgiserver.set_interface(esp)
        print("Starting server")

        self.server.start()
        ip_int = ".".join(str(int(n)) for n in esp.ip_address)
        print(f"IP Address is {ip_int}")

    def reconnect(self):
        self.wifi.connect()
        self.server.start()

    def data(self, request):

        return (
            200,
            [("Content-Type", "application/json")],
            [
                json.dumps(
                    {
                        "value": self.last_value,
                        "time": self.last_time - self.start_time,
                    }
                )
            ],
        )

    def index(self, request):
        # serve the live graph
        with open("graphing.html") as fd:
            return 200, [("Content-Type", "text/html")], [fd.read()]
            
    def update(self):
        # calculate time delta
        new_time = time.monotonic()
        time_delta = new_time - self.last_time
        self.last_time = new_time

        self.last_value += random.randint(-100, 100) * 0.01 * time_delta
        if self.last_value > 1:
            self.last_value = 1
        if self.last_value < -1:
            self.last_value = -1

    def main_loop(self):
        while True:
            try:
                self.update()
                self.server.update_poll()
            except RuntimeError as e:
                traceback.print_exception(BaseException, e, e.__traceback__)
                self.wifi.reset()
                self.reconnect()
                print("Reset complete.")

    def start(self):
        app = WSGIApp()
        app.route("/")(self.index)
        app.route("/data")(self.data)
        print("Starting")
        self.setup_wifi(app)
        self.main_loop()


RandomWalkSensors().start()
