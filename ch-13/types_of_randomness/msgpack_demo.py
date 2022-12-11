from ulab import numpy as np
import random
import msgpack
from io import BytesIO

data = np.array([[random.uniform(-200, 200), random.uniform(-200, 200), random.uniform(0, 360)] for i in range(20)], dtype=np.int16)
print(data)
print(data.shape)
buffer = BytesIO()
msgpack.pack({"offset": 10, "poses": data.tolist()},  buffer)
buffer.seek(0)
print(len(buffer.getvalue())) # json is 618 bytes, msgpack is 595 bytes. msgpack is 3.7% smaller
print(buffer.getvalue())

import json
as_int = np.array(data, dtype=np.int16)
as_int_json = json.dumps({"offset": 10, "poses": as_int.tolist()})


## on pc
import msgpack
import numpy as np
raw_data = "bytes from robot"
data = msgpack.unpackb(raw_data)
poses = np.array(data["poses"])
print(poses)
# Avoiding the text could make it smaller.
# From https://learn.adafruit.com/introducing-the-adafruit-bluefruit-le-uart-friend/hardware
# Note that we do not recommend using higher baudrates than 9600 because the nRF51 UART can drop characters!
# Is the complexity of the msgpack worth the 3.7% size reduction?

