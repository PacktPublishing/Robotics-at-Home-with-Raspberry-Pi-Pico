""" Turn JSON data stream into graphs"""
import requests

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

url = "http://192.168.1.128"


class AnimatedGraph:
    def __init__(self):
        self.fields = {}
        self.samples = 100
        self.reset()

    def reset(self):
        for field in self.fields:
            self.fields[field] = []

    def make_frame(self, frame):
        try:
            response = requests.get(url, timeout=1)
        except requests.exceptions.RequestException:
            print("Waiting...")
            return
        print(f"Content: {response.content}")
        print(f"status: {response.status_code}")

        item = response.json()

        if 'time' in self.fields and item["time"] < self.fields['time'][-1]:
            self.reset()
        for field in item:
            if field not in self.fields:
                self.fields[field] = []
            self.fields[field].append(item[field])

        if len(self.fields['time'] ) > self.samples:
            for field in self.fields:
                self.fields[field] = self.fields[field][-self.samples:]

        plt.cla()  # clear axes.
        # plot the items
        for field in self.fields:
            if field != "time":
                plt.plot("time", field, data=self.fields)

        plt.legend(loc="upper right")

# Create the animation. gcf - get current figure. random_stream - callback func.
animation = FuncAnimation(plt.gcf(), AnimatedGraph().make_frame, interval=200)
plt.tight_layout()
plt.show()
