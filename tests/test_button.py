import utime

from machine import Pin

button = Pin(15, Pin.IN, Pin.OUT)

def button_handler(pin):
    print("!")
    utime.sleep(1)

button.irq(handler=button_handler, trigger=Pin.IRQ_FALLING)

while True:
    print("Running")
    utime.sleep(1)