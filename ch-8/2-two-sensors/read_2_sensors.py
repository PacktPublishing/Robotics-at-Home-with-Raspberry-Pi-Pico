import time
import board
import busio
import adafruit_vl53l1x

i2c0 = busio.I2C(sda=board.GP0, scl=board.GP1)
i2c1 = busio.I2C(sda=board.GP2, scl=board.GP3)

## If you accidentally pass the same bus twice, you'll get the same measurements
vl53_r = adafruit_vl53l1x.VL53L1X(i2c0)
vl53_l = adafruit_vl53l1x.VL53L1X(i2c1)


# we want it short range
vl53_l.distance_mode = 1
vl53_l.timing_budget = 100

vl53_r.distance_mode = 1
vl53_r.timing_budget = 100

vl53_l.start_ranging()
vl53_r.start_ranging()


while True:
    if vl53_l.data_ready and vl53_r.data_ready:
        print("Left: {} cm, Right: {} cm".format(vl53_l.distance, vl53_r.distance))
        vl53_l.clear_interrupt()
        vl53_r.clear_interrupt()
    time.sleep(0.05)
