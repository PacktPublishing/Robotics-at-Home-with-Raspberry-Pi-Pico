import adafruit_bno055
import board
import busio
import time

i2c = busio.I2C(sda=board.GP0, scl=board.GP1)
imu = adafruit_bno055.BNO055_I2C(i2c)

def check_status():
  sys_status, gyro, accel, mag = imu.calibration_status
  print(f"Sys: {sys_status}, Gyro: {gyro}, Accel: {accel}, Mag: {mag}")
  return sys_status == 3

while not check_status():
  time.sleep(0.1)

while True:
  data = {"temperature": imu.temperature, 
          "acceleration": imu.acceleration, 
          "magnetic": imu.magnetic, 
          "gyro": imu.gyro,
          "euler": imu.euler}
  print(data)
  time.sleep(0.1)
