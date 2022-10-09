import adafruit_bno055
import board
import busio

i2c = busio.I2C(sda=board.GP0, scl=board.GP1)
sensor = adafruit_bno055.BNO055_I2C(i2c)

print("Temperature: {} degrees C".format(sensor.temperature))
