import asyncio
import json
import matplotlib.pyplot as plt

from robot_ble_connection import BleConnection


class RobotDisplay:
    def __init__(self):
        self.ble_connection = BleConnection(self.handle_data)
        self.line = ""
        self.arena = {}
        self.display_closed = False
        self.fig, self.ax = plt.subplots()

    def handle_close(self, _):
        self.display_closed = True

    def handle_data(self, data):
        self.line += data.decode("utf-8")
        while "\n" in self.line:
            line, self.line = self.line.split("\n", 1)
            print(f"Received data: {line}")
            try:
                message = json.loads(line)
            except ValueError:
                print("Error parsing JSON")
                return
            if "arena" in message:
                self.arena = message

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

    async def main(self):
        plt.ion()
        await self.ble_connection.connect()
        try:
            request = json.dumps({"command": "arena"}).encode()
            print(f"Sending request for arena: {request}")
            await self.ble_connection.send_uart_data(request)
            self.fig.canvas.mpl_connect("close_event", self.handle_close)

            while not self.display_closed:
                self.draw()
                plt.draw()
                plt.pause(0.05)
                await asyncio.sleep(0.01)
        finally:
            await self.ble_connection.close()


robot_display = RobotDisplay()
asyncio.run(robot_display.main())
