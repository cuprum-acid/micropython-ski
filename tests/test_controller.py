import esp32
import machine
import utime


from machine import Pin
from src.controller import Controller


CONTROLLER = Controller()
LAST_TIME_BUTTON_PRESSED = -100000
BUTTON_TIME_EPS_MS = 3000 # increase if button triggers twice on one press
MODE = 0


def button_handler(pin):
    global LAST_TIME_BUTTON_PRESSED, BUTTON_TIME_EPS_MS, CONTROLLER, MODE

    t = utime.ticks_ms()
    if t - LAST_TIME_BUTTON_PRESSED <= BUTTON_TIME_EPS_MS:
        return
    print(f"Interrupt on pin {pin}, time: {t}")
    LAST_TIME_BUTTON_PRESSED = utime.ticks_ms()
    
    MODE = (MODE + 1) % 5
    if MODE == 0:
        print("Sleeping zzz")
        utime.sleep(5)
        print("Real sleeping")
        utime.sleep(2)
        machine.lightsleep()
    elif MODE == 1:
        print("Idle")
    elif MODE == 2:
        print("Preparing")
        CONTROLLER.prepare_run()
    elif MODE == 3:
        print("Running")
        CONTROLLER.main_cycle() # broken rn (((((( can't exit on button press
        # probably need changes in controller
    elif MODE == 4:
        print("Transmit data")
        CONTROLLER.transmit_data()

button = Pin(15, Pin.IN, Pin.OUT)
button.irq(handler=button_handler, trigger=Pin.IRQ_RISING)

# wakes up from lightsleep on button press
esp32.wake_on_ext0(pin=button, level=esp32.WAKEUP_ANY_HIGH)

cnt = 0
while True:
    print(f"Main loop tick {cnt}")
    cnt += 1
    utime.sleep(1)
