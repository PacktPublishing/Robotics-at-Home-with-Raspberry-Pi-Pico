import time
import json

from adafruit_esp32spi import adafruit_esp32spi_wsgiserver
from adafruit_wsgi.wsgi_app import WSGIApp

import robot
import robot_wifi
import pid


class SpeedControlApp:
    def __init__(self):
        self.wifi = None
        self.server = None

        self.intended_speed = 0.9
        self.last_time = time.monotonic()
        self.speed_to_encoder_factor = 1/5100

        self.left_speed_pid = pid.PID(0, -0.7, 0, self.intended_speed)
        self.right_speed_pid = pid.PID(0, -0.7, 0, self.intended_speed)
        self.left_pid_output = 0
        self.right_pid_output = 0
        self.left_speed = 0
        self.right_speed = 0


    def setup_wifi(self, app):
        print("Setting up wifi.")
        self.wifi, esp = robot_wifi.connect_to_wifi()
        self.server = adafruit_esp32spi_wsgiserver.WSGIServer(80, application=app)
        adafruit_esp32spi_wsgiserver.set_interface(esp)
        print("Starting server")

        self.server.start()
        ip_int = ".".join(str(int(n)) for n in esp.ip_address)
        print(f"IP Address is {ip_int}")

    def update(self):
        new_time = time.monotonic()
        time_delta = new_time - self.last_time
        self.last_time = new_time

        self.left_speed = robot.left_encoder.get_speed(time_delta) * self.speed_to_encoder_factor
        self.right_speed = robot.right_encoder.get_speed(time_delta) * self.speed_to_encoder_factor

        self.left_pid_output = self.left_speed_pid.update(self.left_speed, time_delta)
        self.right_pid_output = self.right_speed_pid.update(self.right_speed, time_delta)

        # print({
        #         "left_speed": self.left_speed,
        #         "left_pid": self.left_pid_output,
        #         "right_speed": self.right_speed,
        #         "right_pid": self.right_pid_output,
        #         "time": self.last_time,
        #         "error_sum": self.left_speed_pid.error_sum
        #     })

        # robot.set_left(self.left_pid_output)
        # robot.set_right(self.right_pid_output)

    def movement_generator(self):
        while True:
            self.update()
            data = json.dumps(
                    {
                        "left_speed": self.left_speed,
                        "left_pid": self.left_pid_output,
                        "right_speed": self.right_speed,
                        "right_pid": self.right_pid_output,
                        "time": self.last_time,
                    }
                ) + "/n"
            print(data)
            yield data

    def index(self, request):
        return (
            200,
            [("Content-Type", "application/json")],
            self.movement_generator(),
        )

    def main_loop(self):
        while True:
            try:
                self.update()

                # time.sleep(0.1)
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


SpeedControlApp().start()
