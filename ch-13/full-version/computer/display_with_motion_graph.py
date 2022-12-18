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
        self.fig, self.ax = plt.subplots()
        self.poses = np.zeros([200, 2], dtype=np.int16)
        self.motion = np.zeros([200, 3], dtype=float)

    def handle_close(self, _):
        self.display_closed = True

    def handle_data(self, data):
        self.line += data.decode("utf-8")
        # print(f"Received data: {data.decode('utf-8')}")
        # print(f"Line is now: {self.line}")
        while "\n" in self.line:
            line, self.line = self.line.split("\n", 1)
            print(f"Received line: {line}")
            try:
                message = json.loads(line)
            except ValueError:
                print("Error parsing JSON")
                return
            if "arena" in message:
                self.arena = message
            if "poses" in message:
                incoming_poses = np.array(message["poses"], dtype=np.int16)
                self.poses = incoming_poses

    def draw(self):
        self.ax.clear()
        if self.arena:
            for line in self.arena["arena"]:
                self.ax.plot(
                    [line[0][0], line[1][0]], [line[0][1], line[1][1]], color="black"
                )                
        self.ax.scatter(self.poses[:,0], self.poses[:,1], color="blue")
        

    async def send_command(self, command):
        #+ "\n" - why does adding this (which sounds right) cause the ble stack (on the robot or computer? ) not to work any more?
        request = (json.dumps({"command": command})  ).encode()
        print(f"Sending request: {request}")
        await self.ble_connection.send_uart_data(request)

    def start(self, _):
        self.button_task = asyncio.create_task(self.send_command("start"))

    # def stop(self, _):
    #     self.button_task = asyncio.create_task(self.send_command("stop"))

    async def main(self):
        plt.ion()
        await self.ble_connection.connect()
        try:
            await self.send_command("arena")
            self.fig.canvas.mpl_connect("close_event", self.handle_close)
            start_button = Button(plt.axes([0.7, 0.05, 0.1, 0.075]), "Start")
            start_button.on_clicked(self.start)
            # stop_button = Button(plt.axes([0.81, 0.05, 0.1, 0.075]), "Stop")
            # stop_button.on_clicked(self.stop)
            while not self.display_closed:
                self.draw()
                plt.draw()
                plt.pause(0.05)
                await asyncio.sleep(0.01)
        finally:
            await self.ble_connection.close()


robot_display = RobotDisplay()
asyncio.run(robot_display.main())
