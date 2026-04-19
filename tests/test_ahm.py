import utime
from machine import Pin, I2C

# I2C for the Wemos D1 Mini with ESP8266
i2c = I2C(scl=Pin(21), sda=Pin(19))

# Create the sensor object using I2C
sensor = ahtx0.AHT20(i2c)

while True:
    print("\nTemperature: %0.2f C" % sensor.temperature)
    print("Humidity: %0.2f %%" % sensor.relative_humidity)
    utime.sleep(5)
