""" Turn JSON data stream into graphs"""
import requests

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

url = 'http://192.168.1.128'


class SensorStream:
  def __init__(self) -> None:
      self.reset()

  def reset(self):
      self.error_values = []
      self.pid_outputs = []
      self.times = []

  def sensor_stream(self, frame):
    response = requests.get(url, timeout=1)
    print(f"Content: {response.content}")
    print(f"status: {response.status_code}")

    item = response.json()
    
    print(f"Received: {item}")
    if self.times and item['time'] < self.times[-1]:
      self.reset()
    self.times.append(item['time'])
    self.error_values.append(item['last_value'])
    self.pid_outputs.append(item['pid_output'])

    if len(self.times) > 100:
        self.times = self.times[-100:]
        self.error_values = self.error_values[-100:]
        self.pid_outputs = self.pid_outputs[-100:]

    plt.cla() # clear axes.
    # plot the items
    plt.plot(self.times, self.error_values, label="error")
    plt.plot(self.times, self.pid_outputs, label="pid")
    
    plt.legend(loc='upper right')

  def start(self):
    # Create the animation. GFC - get current figure. random_stream - callback func.
    self.ani = FuncAnimation(plt.gcf(), self.sensor_stream, interval=200)
    plt.tight_layout()
    plt.show()

SensorStream().start()
