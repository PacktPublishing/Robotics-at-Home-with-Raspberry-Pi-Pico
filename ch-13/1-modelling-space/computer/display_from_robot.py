import asyncio
import json

import matplotlib.pyplot as plt

from robot_ble_connection import BleConnection


class RobotDisplay:
    def __init__(self):
        self.ble_connection = BleConnection(self.handle_data)
        self.line = ""

        self.display_closed = False

    def handle_close(self, _):
        self.display_closed = True

    def handle_data(self, data):
        self.line += data.decode("utf-8")
        if not self.line.endswith("\n"):
            return
        print(f"Received data: {self.line}")
        message = json.loads(self.line)
        self.line = ""
        if "arena" in message:
            self.update_arena(message)

    def update_arena(self, arena):
        plt.gca().clear()
        for line in arena["arena"]:
            plt.gca().plot(
                [line[0][0], line[1][0]], [line[0][1], line[1][1]], color="black"
            )
        for line in arena["target_zone"]:
            plt.gca().plot(
                [line[0][0], line[1][0]], [line[0][1], line[1][1]], color="red"
            )

    async def main(self):
        plt.ion()

        try:
            await self.ble_connection.connect()
            request = json.dumps({"command": "arena"}).encode()
            print(f"Sending request for arena: {request}")
            await self.ble_connection.send_uart_data(request)
            plt.gcf().canvas.mpl_connect("close_event", self.handle_close)

            while not self.display_closed:
                plt.pause(0.05)
                plt.draw()
                await asyncio.sleep(0.01)

            plt.show()
        finally:
            await self.ble_connection.close()


robot_display = RobotDisplay()
asyncio.run(robot_display.main())
