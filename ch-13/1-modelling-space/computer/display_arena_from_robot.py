import asyncio
import json

import matplotlib.pyplot as plt

from robot_ble_connection import BleConnection


class RobotDisplay:
    def __init__(self):
        self.fig, self.ax = plt.subplots()
        self.ble_connection = BleConnection(self.handle_data)

        self.arena = None
        self.display_closed = False
        # handle closed event
        self.fig.canvas.mpl_connect("close_event", self.handle_close)
        self.line = ""

    def handle_close(self, _):
        self.display_closed = True

    def handle_data(self, data):
        line_part = data.decode("utf-8")
        self.line += line_part
        if not self.line.endswith("\n"):
            return
        print(f"Received data: {self.line}")
        data = json.loads(self.line)
        self.line = ""
        if "arena" in data:
            self.update(data)

    def update(self, arena):
        self.arena = arena
        self.ax.clear()
        for line in arena["arena"]:
            self.ax.plot(
                [line[0][0], line[1][0]], [line[0][1], line[1][1]], color="black"
            )
        for line in arena["target_zone"]:
            self.ax.plot(
                [line[0][0], line[1][0]], [line[0][1], line[1][1]], color="red"
            )

    async def main(self):
        plt.ion()

        try:
            await self.ble_connection.connect()
            request = json.dumps({"type": "arena"}).encode()
            print(f"Sending request for arena: {request}")
            self.ble_connection.send_uart_data(request)

            while not self.display_closed:
                plt.pause(0.05)
                plt.draw()
                await asyncio.sleep(0.01)

            plt.show()
        finally:
            await self.ble_connection.close()


robot_display = RobotDisplay()
asyncio.run(robot_display.main())
