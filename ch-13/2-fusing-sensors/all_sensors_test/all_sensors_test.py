import time
import json

from adafruit_esp32spi import adafruit_esp32spi_wsgiserver
from adafruit_wsgi.wsgi_app import WSGIApp

import robot
import robot_wifi
import pid


class AllSensorsApp:
    def __init__(self):
        self.wifi = None
        self.server = None

        self.intended_speed = 0.9
        self.speed_to_encoder_factor = 1/5000
        self.left_speed_pid = pid.PID(0, -0.7, 0, self.intended_speed)
        self.right_speed_pid = pid.PID(0, -0.7, 0, self.intended_speed)
        self.start_time = time.monotonic()
        self.last_time = self.start_time

        self.left_dist = 0
        self.right_dist = 0
        self.left_pid_output = 0
        self.right_pid_output = 0
        self.left_speed = 0
        self.right_speed = 0

    # def setup_robot(self):
    #     robot.left_distance.distance_mode = 1
    #     robot.right_distance.distance_mode = 1

    def setup_wifi(self, app):
        print("Setting up wifi.")
        self.wifi, esp = robot_wifi.connect_to_wifi()
        self.server = adafruit_esp32spi_wsgiserver.WSGIServer(80, application=app)
        adafruit_esp32spi_wsgiserver.set_interface(esp)
        print("Starting server")

        self.server.start()
        ip_int = ".".join(str(int(n)) for n in esp.ip_address)
        print(f"IP Address is {ip_int}")

    def data(self, request):
        imu_data = robot.imu.euler

        return (
            200,
            [("Content-Type", "application/json")],
            [
                json.dumps(
                    {
                        "left_speed_pid": self.left_pid_output,
                        "right_speed_pid": self.right_pid_output,
                        "imu_z": imu_data[2],
                        "left_speed": self.left_speed,
                        "right_speed": self.right_speed,
                        "left_distance": self.left_dist,
                        "right_distance": self.right_dist,
                        "time": self.last_time - self.start_time,
                    }
                )
            ],
        )

    def index(self, request):
        # serve the live graph
        with open("graphing.html") as fd:
            return 200, [("Content-Type", "text/html")], [fd.read()]
            
    def movement_update(self):
        # calculate time delta
        new_time = time.monotonic()
        time_delta = new_time - self.last_time
        self.last_time = new_time

        self.left_speed = robot.left_encoder.get_speed(time_delta) * self.speed_to_encoder_factor
        self.right_speed = robot.right_encoder.get_speed(time_delta) * self.speed_to_encoder_factor

        self.left_pid_output = self.left_speed_pid.update(self.left_speed, time_delta)
        self.right_pid_output = self.right_speed_pid.update(self.right_speed, time_delta)
        
        # robot.set_left(self.left_pid_output)
        # robot.set_right(self.right_pid_output)

        # # do we have data
        # if robot.left_distance.data_ready:
        #     self.left_dist = robot.left_distance.distance
        #     self.right_dist = robot.right_distance.distance

        #     # reset and loop
        #     robot.left_distance.clear_interrupt()
        #     robot.right_distance.clear_interrupt()

    def main_loop(self):
        # robot.left_distance.start_ranging()
        # robot.right_distance.start_ranging()
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
        app.route("/data")(self.data)
        print("Starting")
        try:
            # self.setup_robot()
            self.setup_wifi(app)
            self.main_loop()
        finally:
            robot.stop()
            # robot.left_distance.clear_interrupt()
            # robot.left_distance.stop_ranging()
            # robot.right_distance.clear_interrupt()
            # robot.right_distance.stop_ranging()


AllSensorsApp().start()
