import asyncio
import json

import arena
import robot

def send_json(data):
    robot.uart.write((json.dumps(data) + "\n").encode())

def read_json():
    data = robot.uart.readline()
    decoded = data.decode()
    return json.loads(decoded)

async def command_handler():
    print("Starting handler")
    while True:
        if robot.uart.in_waiting:
            request = read_json()
            print("Received: ", request)
            # {"command": "arena"}
            if request["command"] == "arena":
                send_json({
                    "arena": arena.boundary_lines,
                })
        await asyncio.sleep(0.1)

asyncio.run(command_handler())
