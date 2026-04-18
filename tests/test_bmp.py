import utime
from machine import Pin, I2C
from bmp280 import BMP280

# I2C for the Wemos D1 Mini with ESP8266
i2c = I2C(scl=Pin(23), sda=Pin(22))

# Create the sensor object using I2C
sensor = BMP280(i2c)

while True:
    print("Pressure: %0.2f Pa" % sensor.pressure)
    utime.sleep(5)