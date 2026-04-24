# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()
from main import Main
from machine import Pin
import esp32
import machine
import utime

START = False
BUTTON = Pin(34, Pin.IN, Pin.PULL_DOWN)
LED_1 = Pin(33, Pin.OUT)
LED_2 = Pin(25, Pin.OUT)


def start_handler(pin):
    global START
    START = True
    
BUTTON.irq(handler=start_handler, trigger=Pin.IRQ_RISING)

if __name__ == "__main__":
    LED_1.off()
    LED_2.off()
    LED_1.toggle()
    while True:
        print("Waiting for start signal")
        LED_1.toggle()
        LED_2.toggle()
        if START:
            BUTTON.irq(handler=None)
            LED_1.off()
            LED_2.off()
            Main()
            break
        utime.sleep(1)
