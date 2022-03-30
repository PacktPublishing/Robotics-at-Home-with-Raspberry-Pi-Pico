import board
import busio
from digitalio import DigitalInOut
from adafruit_esp32spi import adafruit_esp32spi
from adafruit_esp32spi import adafruit_esp32spi_wifimanager

try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise


def connect_to_wifi():
    esp32_cs = DigitalInOut(board.GP10)
    esp32_ready = DigitalInOut(board.GP9)
    esp32_reset = DigitalInOut(board.GP8)

    spi = busio.SPI(board.GP14, MOSI=board.GP11, MISO=board.GP12)
    esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
    esp.reset()
    wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, secrets)
    wifi.connect()

    return wifi, esp
