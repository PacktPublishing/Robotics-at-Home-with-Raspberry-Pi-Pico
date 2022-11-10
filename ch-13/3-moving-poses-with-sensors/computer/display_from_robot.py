import asyncio
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

from robot_ble_connection import BleConnection


class RobotDisplay:
    def __init__(self):
        self.ble_connection = BleConnection(self.handle_data)
        self.line = ""
        self.arena = {}
        self.display_closed = False
        self.pose_coords = np.array([(0,), (0,)])
        self.pose_uv = np.array([(1,), (1,)])

    def handle_close(self, _):
        self.display_closed = True

    def handle_data(self, data):
        self.line += data.decode("utf-8")
        while "\n" in self.line:
            line, self.line = self.line.split("\n", 1)
            print(f"Received data: ```{line}```")
            try:
                message = json.loads(line)
            except ValueError:
                print("Error parsing JSON")
                return

            if "arena" in message:
                self.arena = message
            if "poses" in message:
                # the robot poses are an array of [x, y, theta] arrays.
                # matplotlib quiver plots wants an array of [x,y] arrays, and a separate array of angles
                poses = np.array(message["poses"]).T
                self.pose_coords = poses[:2]
                angle_rads = np.deg2rad(poses[2])
                self.pose_uv = np.array([np.cos(angle_rads), np.sin(angle_rads)])
 
    def draw(self):
        self.ax.clear()
        if self.arena:
            for line in self.arena["arena"]:
                self.ax.plot(
                    [line[0][0], line[1][0]], [line[0][1], line[1][1]], color="black"
                )
            for line in self.arena["target_zone"]:
                self.ax.plot(
                    [line[0][0], line[1][0]], [line[0][1], line[1][1]], color="red"
                )
        if len(self.pose_coords) > 0:
            self.ax.quiver(self.pose_coords[0], self.pose_coords[1], self.pose_uv[0], self.pose_uv[1], color="blue")

    async def send_command(self, command):
        request = json.dumps({"command": command}).encode()
        print(f"Sending request: {request}")
        await self.ble_connection.send_uart_data(request)

    def start(self, _):
        self.button_task = asyncio.create_task(self.send_command("start"))

    def stop(self, _):
        self.button_task = asyncio.create_task(self.send_command("stop"))

    async def main(self):
        plt.ion()
        await self.ble_connection.connect()
        try:
            # await self.send_command("arena")
            self.fig, self.ax = plt.subplots()
            self.fig.canvas.mpl_connect("close_event", self.handle_close)
            start_button = Button(plt.axes([0.7, 0.05, 0.1, 0.075]), "Start")
            start_button.on_clicked(self.start)
            stop_button = Button(plt.axes([0.81, 0.05, 0.1, 0.075]), "Stop")
            stop_button.on_clicked(self.stop)

            while not self.display_closed:
                self.draw()
                plt.pause(0.05)
                await asyncio.sleep(0.01)

                plt.draw()
        finally:
            await self.ble_connection.close()


robot_display = RobotDisplay()
asyncio.run(robot_display.main())
