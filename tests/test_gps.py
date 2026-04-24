# Code for ESP32 or Pico using micropyGPS
from machine import UART
import time
from micropyGPS import MicropyGPS

# Setup UART for NEO-6M
# For ESP32, use UART(2) with pins 16(RX) and 17(TX)
gps_module = UART(2, baudrate=9600, tx=17, rx=16)
# For Pico, use UART(1) with pins 4(TX) and 5(RX)
# gps_module = UART(1, baudrate=9600, tx=4, rx=5)

# Initialize the GPS parser
my_gps = MicropyGPS()

print("Waiting for GPS fix...")
while True:
    if gps_module.any():
        data = gps_module.read(1)  # Read one character at a time
        # Decode the single byte and feed it to the parser
        stat = my_gps.update(chr(data[0]))
        
        # When a full sentence is parsed, 'stat' will contain its type (e.g., 'GPRMC')
        if stat:
            print('Found a sentence:', stat)
            # Check if the GPS has a valid fix (latitude is not 0.0)
            if my_gps.latitude[0] != 0.0:
                print('Timestamp (UTC):', my_gps.timestamp)
                print('Date:', my_gps.date_string('long'))
                print('Latitude:', my_gps.latitude_string())
                print('Longitude:', my_gps.longitude_string())
                print('Altitude:', my_gps.altitude)
                print('Speed (km/h):', my_gps.speed_string('kph'))
                print('---')