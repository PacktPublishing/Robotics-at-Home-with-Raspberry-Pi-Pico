import board
import busio
from digitalio import DigitalInOut
from adafruit_esp32spi import adafruit_esp32spi
import time


print("ESP32 SPI hardware test")

esp32_cs = DigitalInOut(board.GP10)
esp32_ready = DigitalInOut(board.GP9)
esp32_reset = DigitalInOut(board.GP8)

spi = busio.SPI(board.GP14, board.GP11, board.GP12)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)

if esp.status == adafruit_esp32spi.WL_IDLE_STATUS:
    print("ESP32 found and in idle mode")
print("Firmware vers.", esp.firmware_version)
print("MAC addr:", [hex(i) for i in esp.MAC_address])
# esp.start_scan_networks()

# time.sleep(5)

for ap in esp.scan_networks():
    print("\t%s\t\tRSSI: %d" % (str(ap["ssid"], "utf-8"), ap["rssi"]))
print("Done!")
