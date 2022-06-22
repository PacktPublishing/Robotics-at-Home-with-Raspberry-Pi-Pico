import board
import busio
from digitalio import DigitalInOut
from adafruit_esp32spi import adafruit_esp32spi
from adafruit_esp32spi import adafruit_esp32spi_wifimanager
from adafruit_esp32spi import adafruit_esp32spi_wsgiserver

try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise


def connect_to_wifi():
    esp32_cs = DigitalInOut(board.GP10)
    esp32_ready = DigitalInOut(board.GP9)
    esp32_reset = DigitalInOut(board.GP8)

    status_led = DigitalInOut(board.LED)
    status_led.switch_to_output()

    print("Starting spi bus...")
    spi = busio.SPI(board.GP14, MOSI=board.GP11, MISO=board.GP12)
    print("Creating ESP SPI control...")
    esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
    # print("Resetting...")
    print("Firmware vers.", esp.firmware_version)
    print("MAC addr:", [hex(i) for i in esp.MAC_address])
    # esp.reset()
    print("Starting Wifi Manager...")
    wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, secrets)
    print("Connecting...")
    wifi.connect()

    status_led.value = 1

    return wifi, esp


def start_wifi_server(app, background_task=None):
    print("Setting up wifi.")
    wifi, esp = connect_to_wifi()
    server = adafruit_esp32spi_wsgiserver.WSGIServer(80, application=app)
    adafruit_esp32spi_wsgiserver.set_interface(esp)

    print("Starting server")

    server.start()
    ip_int = ".".join(str(int(n)) for n in esp.ip_address)
    print(f"IP Address is {ip_int}")
    while True:
        try:
            server.update_poll()
            # background task
            if background_task:
                background_task()
        except ConnectionError:
            print("Connection error detected. Carrying on")
        except:
            print("Shutting down wifi on failure. resetting ESP")
            wifi.reset()
            raise
