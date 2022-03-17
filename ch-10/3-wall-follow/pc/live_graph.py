""" Turn JSON data stream into graphs"""
from itertools import count

import requests

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

url = 'http://192.168.1.128'


class SensorStream:
  def __init__(self) -> None:
      self.index = count()
      self.error_values = []
      self.sensor_values = []
      self.pid_outputs = []
      self.x_values = []

      self.set_point = requests.get(f"{url}/set_point").json()

  def sensor_stream(self):
    item = requests.get(url).json()
    print(f"Received: {item.decode('utf-8')}")
    self.x_vals.append(next(self.index))
    self.error_values.append(item['error_value'])
    self.sensor_values.append(item['sensor_value'])
    self.pid_outputs.append(item['pid_output'])

    if len(self.x_vals) > 100:
        self.x_vals = self.x_vals[-100:]
        
        self.error_values = self.error_values[-100:]
        self.sensor_values = self.sensor_values[-100:]
        self.pid_outputs = self.pid_outputs[-100:]

    plt.cla() # clear axes.
    # plot the items
    plt.plot(self.x_vals, self.error_values, label="error")
    plt.plot(self.x_vals, self.sensor_values, label="sensor")
    plt.plot(self.x_vals, self.pid_outputs, label="pid")
    
    plt.legend(loc='upper right')

  def start(self):
    plt.style.use('fivethirtyeight')
    # Create the animation. GFC - get current figure. random_stream - callback func.
    self.ani = FuncAnimation(plt.gcf(), self.sensor_stream, interval=200)
    plt.tight_layout()
    plt.show()

SensorStream().start()
