import time
import json

from adafruit_esp32spi import adafruit_esp32spi_wsgiserver
from adafruit_wsgi.wsgi_app import WSGIApp

import robot
import robot_wifi


class SpeedCountApp:
    def __init__(self):
        self.intended_speed = 0.9
        self.last_time = time.monotonic()
        self.wifi = None
        self.server = None

    def setup_wifi(self, app):
        print("Setting up wifi.")
        self.wifi, esp = robot_wifi.connect_to_wifi()
        self.server = adafruit_esp32spi_wsgiserver.WSGIServer(80, application=app)
        adafruit_esp32spi_wsgiserver.set_interface(esp)
        print("Starting server")

        self.server.start()
        ip_int = ".".join(str(int(n)) for n in esp.ip_address)
        print(f"IP Address is {ip_int}")

    def index(self, request):
        new_time = time.monotonic()
        time_delta = new_time - self.last_time
        self.last_time = new_time

        left_speed = robot.left_encoder.get_speed(time_delta)
        right_speed = robot.right_encoder.get_speed(time_delta)
        return (
            200,
            [("Content-Type", "application/json")],
            [
                json.dumps(
                    {
                        "left_speed": left_speed,
                        "right_speed": right_speed,
                        "time": self.last_time,
                    }
                )
            ],
        )

    def main_loop(self):
        robot.set_left(self.intended_speed)
        robot.set_right(self.intended_speed)
        while True:
            try:
                self.server.update_poll()
            except RuntimeError as e:
                print(f"Server poll error: {type(e)}, {e}")
                print(f"Resetting ESP...")
                self.wifi.reset()
                print("Reset complete.")

    def start(self):
        app = WSGIApp()
        app.route("/")(self.index)
        print("Starting")
        try:
            self.setup_wifi(app)
            self.main_loop()
        finally:
            robot.stop()


SpeedCountApp().start()
