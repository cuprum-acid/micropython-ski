import ahtx0
import os
import utime

from bmp280 import BMP280
from machine import I2C, Pin
from mpu6500 import MPU6500


class Controller():
    def __init__(self):
        self.DATA_DIR = "data/"
        try:
            os.mkdir(self.DATA_DIR)
        except Exception:
            pass

        self.filename = None
        self.mpu_sensor = None
        self.bmp_sensor = None
        self.button = Pin(15, Pin.IN, Pin.OUT)

        self.is_prepared = True  # TODO: change later (GPS, magnetometer)
        self.run_measurement = False
        self.button.irq(handler=self._button_handler, trigger=Pin.IRQ_RISING)

    def _button_handler(pin):
        self.run_measurement = False

    def perform_measurement(self):
        # assert self.mpu_sensor is not None and self.bmp_sensor is not None

        time = utime.ticks_ms()
        gyro = self.mpu_sensor.gyro
        acceleration = self.mpu_sensor.acceleration
        pressure = self.bmp_sensor.pressure
        # Check which temp is better, maybe avg
        return time, gyro, acceleration, pressure

    def check_temperature_and_humidity(self):
        ahm_sensor = ahtx0.AHT20(I2C(scl=Pin(21), sda=Pin(19)))
        temperature = ahm_sensor.temperature
        humidity = ahm_sensor.relative_humidity

        # if we don't reinit mpu and bmp after we'll get OSError
        # probably due to ahtx and mpu/bmp using same addresses as ahtx
        return temperature, humidity

    def prepare_run(self):
        # TODO: change later (GPS, magnetometer)
        self.is_prepared = True

    def transmit_data(self):
        pass  # TODO: wifi connection

    def _init_gyro_accel(self):  # TODO: change naming
        i2c = I2C(scl=Pin(23), sda=Pin(22))
        self.mpu_sensor = MPU6500(i2c)
        self.bmp_sensor = BMP280(i2c)

    def _write_metadata(self):
        t = utime.gmtime()
        timestamp = "{:04d}-{:02d}-{:02d}_{:02d}-{:02d}-{:02d}".format(
            t[0], t[1], t[2], t[3], t[4], t[5]
        )
        self.filename = self.DATA_DIR + timestamp + ".txt"

        with open(self.filename, "w") as f:
            f.write("Metadata section\n")
            f.write(f"timestamp: {timestamp}\n")
            temperature, humidity = self.check_temperature_and_humidity()

            f.write(f"humidity: {humidity}\n")
            f.write(f"temperature: {temperature}\n")

            self._init_gyro_accel()  # if we don't reinit we get OSError
            f.write(f"temperature2: {self.mpu_sensor.temperature}\n")
            f.write(f"temperature3: {self.bmp_sensor.temperature}\n")

            gyro_offset = self.mpu_sensor.calibrate()
            f.write(f"gyro_offset_xyz: {gyro_offset[0]}, {gyro_offset[1]} {gyro_offset[2]}\n")
            f.write(f"gyro_sf: {self.mpu_sensor._gyro_sf}\n")
            f.write(f"accel_sf: {self.mpu_sensor._accel_sf}\n")
            f.write(f"gyro_so: {self.mpu_sensor._gyro_so}\n")
            f.write(f"accel_so: {self.mpu_sensor._accel_so}\n")

            f.write(f"\nData section\n")

    def main_cycle(self):
        if not self.is_prepared:
            print("Device not set up")
            return

        self._write_metadata()
        cnt = 0
        self.run_measurement = True
        with open(self.filename, "a") as f:
            f.write("time gyro_x gyro_y gyro_z accel_x accel_y accel_z pressure\n")
            while self.run_measurement and cnt < 10_000:  # fix, rn can't exit this cycle on button press
                data = self.perform_measurement()
                f.write(
                    f"{data[0]} {data[1][0]} {data[1][1]} {data[1][2]} {data[2][0]} {data[2][1]} {data[2][2]} {data[3]}\n")
                print(data)
                cnt += 1


if __name__ == "__main__":
    controller = Controller()
    controller.prepare_run()
    controller.main_cycle()
