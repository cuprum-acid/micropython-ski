from machine import Pin
import utime

 

cnt = 0
while True:
    cnt += 1
    print(f"tick {cnt}")
    if cnt == 10:
        en_pin = Pin(9, Pin.OUT)
        en_pin.high()
        
    utime.sleep(1)
    