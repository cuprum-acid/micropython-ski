import utime

from machine import Pin

button = Pin(35, Pin.IN, Pin.PULL_DOWN)

def button_handler(pin):
    print("!")
    utime.sleep(1)

button.irq(handler=button_handler, trigger=Pin.IRQ_FALLING)

while True:
    print("Running")
    utime.sleep(1)