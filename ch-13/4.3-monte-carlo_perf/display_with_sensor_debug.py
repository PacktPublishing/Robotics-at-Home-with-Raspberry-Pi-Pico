import asyncio
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

from robot_ble_connection import BleConnection


class RobotDisplay:
    def __init__(self):
        self.ble_connection = BleConnection(self.handle_data)
        self.buffer = ""
        self.arena = {}
        self.closed = False
        self.fig, self.axes = plt.subplots()
        self.poses = None
        self.distance_observation = None

    def handle_close(self, _):
        self.closed = True

    def handle_data(self, data):
        self.buffer += data.decode()
        # print(f"Received raw data: {data}")
        while "\n" in self.buffer:
            line, self.buffer = self.buffer.split("\n", 1)
            print(f"Received data: {line}")
            try:
                message = json.loads(line)
            except ValueError:
                print("Error parsing JSON")
                return
            if "arena" in message:
                self.arena = message
            if "poses" in message:
                self.poses = np.array(message["poses"], dtype=np.int16)
            if "distance_observation" in message:
                self.distance_observation = message["distance_observation"]

    def draw(self):
        self.axes.clear()
        if self.arena:
            for line in self.arena["arena"]:
                self.axes.plot(
                    [line[0][0], line[1][0]], [line[0][1], line[1][1]], color="black"
                )
        if self.poses is not None:
            self.axes.scatter(self.poses[:,0], self.poses[:,1], color="blue")
        if self.distance_observation:
            # draw a red arrow from the distance observation pose (in its direction)
            heading = np.radians(self.distance_observation["pose"][2])
            self.axes.arrow(
                self.distance_observation["pose"][0],
                self.distance_observation["pose"][1],
                100 * np.cos(heading),
                100 * np.sin(heading),
                color="red",
            )
            # draw yellow dot at the left distance sensor location
            self.axes.scatter(
                self.distance_observation["left_sensor"][0],
                self.distance_observation["left_sensor"][1],
                color="yellow",
            )
            # draw yellow dot at the right distance sensor location
            self.axes.scatter(
                self.distance_observation["right_sensor"][0],
                self.distance_observation["right_sensor"][1],
                color="yellow",
            )
            # write the weight of the distance observation as text below the arrow
            self.axes.text(
                self.distance_observation["pose"][0],
                self.distance_observation["pose"][1],
                f"{self.distance_observation['weight']:.2E}",
            )

    async def send_command(self, command):
        request = (json.dumps({"command": command})  ).encode()
        print(f"Sending request: {request}")
        await self.ble_connection.send_uart_data(request)

    def start(self, _):
        self.button_task = asyncio.create_task(self.send_command("start"))

    async def main(self):
        plt.ion()
        await self.ble_connection.connect()
        try:
            await self.send_command("arena")
            self.fig.canvas.mpl_connect("close_event", self.handle_close)
            start_button = Button(plt.axes([0.7, 0.05, 0.1, 0.075]), "Start")
            start_button.on_clicked(self.start)
            while not self.closed:
                self.draw()
                plt.draw()
                plt.pause(0.05)
                await asyncio.sleep(0.01)
        finally:
            await self.ble_connection.close()


robot_display = RobotDisplay()
asyncio.run(robot_display.main())
