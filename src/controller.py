import ahtx0
import utime

from machine import I2C, Pin
from mpu6500 import MPU6500


class Controller():
    def __init__(self):
        self.DATA_DIR = "data/" # create if not exists
        self.filename = None
        self.mpu_sensor = None
        
    def step(self):        
        # temperature = self.mpu_sensor.temperature
        time = utime.ticks_us() # time nanosec
        gyro = self.mpu_sensor.gyro
        acceleration = self.mpu_sensor.acceleration
        # Check which temp is better, maybe avg
        return time, gyro, acceleration
    
    def check_temperature_and_humidity(self):
        ahm_sensor = ahtx0.AHT20(I2C(scl=Pin(21), sda=Pin(19)))
        temperature = ahm_sensor.temperature
        humidity = ahm_sensor.relative_humidity
        return temperature, humidity
        
    
    def prepare_run(self):
        t = utime.gmtime()
        timestamp = "{:04d}-{:02d}-{:02d}_{:02d}-{:02d}-{:02d}".format(
            t[0], t[1], t[2], t[3], t[4], t[5]
        )
        self.filename = self.DATA_DIR + timestamp + ".txt"
        
        with open(self.filename, "w") as f:
            f.write("Metadata section\n")
            f.write(f"Timestamp: {timestamp}\n")
            temperature, humidity = self.check_temperature_and_humidity()
            f.write(f"Temperature: {temperature}\n")
            f.write(f"Humidity: {humidity}\n")
            
            # mpu settings
            self.mpu_sensor = MPU6500(I2C(scl=Pin(23), sda=Pin(22)))
            gyro_offset = self.mpu_sensor.calibrate()
            f.write(f"gyro_offset: {gyro_offset}\n")
            
            
            f.write(f"\nData section\n")
            
        pass
    
    def main_cycle(self):        
        cnt = 0
        with open(self.filename, "a") as f:
            while cnt < 10:
                data = self.step()
                f.write("{" + f"timestamp: {data[0]}, gyro:{data[1]}, acceleration: {data[2]}" + "}\n")
                print(data)
                cnt += 1
            

controller = Controller()
controller.prepare_run()
controller.main_cycle()
