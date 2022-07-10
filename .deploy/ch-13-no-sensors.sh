rm -rf /volumes/CIRCUITPY/lib/adafruit_espi

rsync -rv libs/Adafruit_CircuitPython_ESP32SPI/adafruit_esp32spi /volumes/CIRCUITPY/lib

.deploy/send-libs.sh \
  adafruit_requests.mpy \
  adafruit_wsgi


.deploy/send-it.sh \
  ch-13/2-fusing-sensors/no_imu/no_sensors.py \
  ch-13/2-fusing-sensors/no_imu/graphing.html \
  ch-13/2-fusing-sensors/no_imu/robot_wifi.py \
  secrets.py
