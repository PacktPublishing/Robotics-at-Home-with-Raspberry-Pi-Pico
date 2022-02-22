import time
import board
import busio
import adafruit_vl53l1x

# i2c = busio.I2C(sda=board.GP0, scl=board.GP1)
i2c = busio.I2C(sda=board.GP2, scl=board.GP3)
vl53 = adafruit_vl53l1x.VL53L1X(i2c)

vl53.distance_mode = 1

vl53.timing_budget = 100
vl53.start_ranging()

while True:
    if vl53.data_ready:
        print("Distance: {} cm".format(vl53.distance))
        vl53.clear_interrupt()
    time.sleep(0.05)
