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

    def handle_close(self, _):
        self.closed = True

    def handle_data(self, data):
        self.buffer += data.decode()
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

    def draw(self):
        self.axes.clear()
        if self.arena:
            for line in self.arena["arena"]:
                self.axes.plot(
                    [line[0][0], line[1][0]], [line[0][1], line[1][1]], color="black"
                )
        if self.poses is not None:
            self.axes.scatter(self.poses[:,0], self.poses[:,1], color="blue")

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
