import ahtx0
import os
import utime

from ahtx0 import AHT20
from bmp280 import BMP280
from machine import I2C, Pin, Timer, UART
from micropyGPS import MicropyGPS
from mpu6500 import MPU6500



class Controller:
    def __init__(self):
        self.DATA_DIR = "data/"
        self.MAX_FILES_CNT = 20
        self.MAX_RUN_TIME_MS = 40000 # 40 sec
        
        try:
            os.mkdir(self.DATA_DIR)
        except Exception:
            pass
        self.META_DIR = "meta/"
        try:
            os.mkdir(self.META_DIR)
            with open(self.META_DIR + 'calibration.txt', 'w') as f:
                f.write('Not calibrated\n')
        except Exception:
            pass
        
        self.clear_data_folder()
        self.filename = None
        self.filename_gps = None

        i2c = I2C(scl=Pin(21), sda=Pin(19))
        self.mpu_sensor = MPU6500(i2c)
        self.bmp_sensor = BMP280(i2c)
        self.aht_sensor = AHT20(i2c)

        self.gps_module = UART(2, baudrate=9600, tx=17, rx=16)
        self.gps_parser = MicropyGPS()
        
        self.is_prepared = True  # TODO: change later (GPS, magnetometer)

        self.run_measurement = False
        self.run_transmit = False
        self.run_prepare = False

        self.accel_sum_x = 0
        self.accel_sum_y = 0
        self.accel_sum_z = 0
        self.accel_sum_n = 0
        
    def clear_data_folder(self):
        '''Keeps latests MAX_FILES_CNT in data and removes all other older files'''
        all_files = os.listdir(self.DATA_DIR)
        all_files.sort(reverse=True)
        print("All files in /data")
        print(*all_files, sep='\n')
        while len(all_files) >= self.MAX_FILES_CNT:
            file = all_files.pop()
            filename = self.DATA_DIR + file
            try:
                print(f"File removed {filename}")
                os.remove(filename)
            except Exception:
                print(f"Error deleting file {file}")
        
    def stop_main_run(self):
        print("Stop cycle")
        self.run_measurement = False
        
    def stop_main_run_timeout(self, timer_obj):
        print("Stop cycle timeout")
        self.run_measurement = False
        
    def stop_prepare(self):
        print("Stop prepare")
        self.run_prepare = False
        
    def stop_transmit(self):
        print("Stop transmit")
        self.run_transmit = False

    def _perform_measurement(self):
        time = utime.ticks_ms()
        gyro = self.mpu_sensor.gyro
        acceleration = self.mpu_sensor.acceleration
        pressure = self.bmp_sensor.pressure
        return time, gyro, acceleration, pressure

    def check_temperature_and_humidity(self):
        temperature = self.aht_sensor.temperature
        humidity = self.aht_sensor.relative_humidity
        return temperature, humidity

    def prepare_run(self):
        # TODO: change later (GPS, magnetometer)
        self.is_prepared = True

    def transmit_data(self):
        self.run_transmit = True
        while self.run_transmit:
            print("Transmitting")
            utime.sleep(1)
            pass  # TODO: wifi connection

    def _write_metadata(self):
        t = utime.gmtime()
        timestamp = "{:04d}-{:02d}-{:02d}_{:02d}-{:02d}-{:02d}".format(
            t[0], t[1], t[2], t[3], t[4], t[5]
        )
        self.filename = self.DATA_DIR + timestamp + ".txt"
        self.filename_gps = self.DATA_DIR + timestamp + "_gps" + ".txt"
        self.clear_data_folder()
        
        with open(self.META_DIR + "calibration.txt", "r") as f:
            calibration_meta = f.readlines()
        
        with open(self.filename, "w") as f:
            f.write("Metadata section\n")
            f.write(f"timestamp: {timestamp}\n")
            temperature, humidity = self.check_temperature_and_humidity()
            
            f.write(f"humidity: {humidity}\n")
            f.write(f"temperature: {temperature}\n")
            
            f.write(f"temperature2: {self.mpu_sensor.temperature}\n")
            f.write(f"temperature3: {self.bmp_sensor.temperature}\n")
            # Check which temp is better, maybe avg

            gyro_offset = self.mpu_sensor.calibrate()
            f.write(f"gyro_offset_xyz: {gyro_offset[0]}, {gyro_offset[1]} {gyro_offset[2]}\n")
            f.write(f"gyro_sf: {self.mpu_sensor._gyro_sf}\n")
            f.write(f"accel_sf: {self.mpu_sensor._accel_sf}\n")
            f.write(f"gyro_so: {self.mpu_sensor._gyro_so}\n")
            f.write(f"accel_so: {self.mpu_sensor._accel_so}\n")
            f.write(''.join(calibration_meta) + '\n')

            f.write(f"\nData section\n")
    
    def get_gps_data(self, time):
        if self.gps_module.any():
            data_gps = self.gps_module.read(1)  # Read one character at a time
            # Decode the single byte and feed it to the parser
            stat = self.gps_parser.update(chr(data_gps[0]))
            if stat:
                with open(self.filename_gps, "a") as f:
                    f.write(f"Ticks: {time}\n")
                    f.write(f'Timestamp (UTC): {self.gps_parser.timestamp}\n')
                    f.write(f"Date: {self.gps_parser.date_string('long')}\n")
                    f.write(f'Latitude: {self.gps_parser.latitude_string()}\n')
                    f.write(f'Longitude: {self.gps_parser.longitude_string()}\n')
                    f.write(f'Altitude: {self.gps_parser.altitude}\n')
                    f.write(f"Speed (km/h): {self.gps_parser.speed_string('kph')}\n")

    def main_cycle(self):
        if not self.is_prepared:
            print("Device not set up")
            return

        self._write_metadata()
        cnt = 0
        self.run_measurement = True
        with open(self.filename, "a") as f:
            f.write("time gyro_x gyro_y gyro_z accel_x accel_y accel_z pressure\n")
            
            timer = Timer(2)
            timer.init(mode=Timer.ONE_SHOT, period=self.MAX_RUN_TIME_MS, callback=self.stop_main_run_timeout)
    
            while self.run_measurement:
                data = self._perform_measurement()
                utime.sleep(0.01)
                f.write(
                    f"{data[0]} {data[1][0]} {data[1][1]} {data[1][2]} {data[2][0]} {data[2][1]} {data[2][2]} {data[3]}\n")
                #print(data)
                self.accel_sum_x += data[2][0]
                self.accel_sum_y += data[2][1]
                self.accel_sum_z += data[2][2]
                self.accel_sum_n += 1
                if cnt % 100 == 0:
                    self.get_gps_data(data[0])
                
                    
                cnt += 1
                # utime.sleep(1)

            timer.deinit()
            print("accel_sum_x accel_sum_y accel_sum_z accel_cnt")
            print(f"{self.accel_sum_x} {self.accel_sum_y} {self.accel_sum_z} {self.accel_sum_n}")


if __name__ == "__main__":
    controller = Controller()
    controller.prepare_run()
    controller.main_cycle()
