import utime
from machine import I2C, Pin
from mpu6500 import MPU6500

i2c = I2C(scl=Pin(23), sda=Pin(22))
sensor = MPU6500(i2c)

print("MPU9250 id: " + hex(sensor.whoami))

while True:
    print(sensor.acceleration)
    print(sensor.gyro)
    print(sensor.temperature)

    utime.sleep_ms(1000)
