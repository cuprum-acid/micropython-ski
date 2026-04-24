import esp32
import machine
import utime

from machine import Pin, Timer
from src.controller import Controller


CONTROLLER = Controller()
LAST_TIME_BUTTON_PRESSED = -100000
BUTTON_PRESS_DELAY_MS = 3000 # increase if button triggers twice on one press
MODE = 5
'''
MODE 0 = sleep
MODE 1 = idle
MODE 2 = prepare run
MODE 3 = main cycle (run)
MODE 4 = transmit data
MODE 5 = waking up
'''
BUTTON_DATA_TRANSFER = Pin(32, Pin.IN, Pin.PULL_DOWN) # idle/transmit button1
BUTTON_PREPARE_RUN = Pin(35, Pin.IN, Pin.PULL_DOWN) # idle/prepare button2
BUTTON_DOWNHILL = Pin(34, Pin.IN, Pin.PULL_DOWN) # sleep/idle/run button3
LED_1 = Pin(33, Pin.OUT)
LED_2 = Pin(25, Pin.OUT)
SLEEP_TIMER = Timer(0)
BLINK_TIME_DERIOD_MS = 1000 # 1 sec
SLEEP_TIME_MS = 300000 # 5 mins

def check_button(pin):
    global LAST_TIME_BUTTON_PRESSED, BUTTON_PRESS_DELAY_MS
    t = utime.ticks_ms()
    if t - LAST_TIME_BUTTON_PRESSED <= BUTTON_PRESS_DELAY_MS:
        return False
    print(f"Interrupt on pin {pin}, time: {t}")
    LAST_TIME_BUTTON_PRESSED = utime.ticks_ms()
    return True

def go_sleep(timer_obj):
    global MODE
    MODE = 0

def button_downhill_handler(pin): # run
    global MODE
    if not check_button(pin):
        return
    if MODE == 1:
        MODE = 3
    elif MODE == 3:
        CONTROLLER.stop_main_run()
        MODE = 1

def button_prepare_handler(pin): # prepare
    global MODE 
    if not check_button(pin):
        return
    if MODE == 1:
        MODE = 2
    elif MODE == 2:
        CONTROLLER.stop_prepare()
        MODE = 1
        
def button_transmit_handler(pin): # transmit
    global MODE
    if not check_button(pin):
        return
    if MODE == 1:
        MODE = 4
    elif MODE == 4:
        CONTROLLER.stop_transmit()
        MODE = 1

def remove_irq(button):
    button.irq(handler=None)
    
def add_irq(button, callback_func):
    button.irq(handler=callback_func, trigger=Pin.IRQ_RISING)

def toggle_led_1(timer_obj):
    global LED_1
    LED_1.toggle()

def toggle_led_2(timer_obj):
    global LED_2
    LED_2.toggle()

def start_sleep_timer(delay_ms=SLEEP_TIME_MS):
    global SLEEP_TIMER
    SLEEP_TIMER.init(mode=Timer.ONE_SHOT, period=delay_ms, callback=go_sleep)
    
def stop_sleep_timer():
    global SLEEP_TIMER
    SLEEP_TIMER.deinit()


def Main():
    global MODE
    LED_1.off()
    LED_2.off()
    add_irq(BUTTON_DATA_TRANSFER, button_transmit_handler)
    add_irq(BUTTON_PREPARE_RUN, button_prepare_handler)
    add_irq(BUTTON_DOWNHILL, button_downhill_handler)

    # wakes up from lightsleep on button press
    esp32.wake_on_ext0(pin=BUTTON_DOWNHILL, level=esp32.WAKEUP_ANY_HIGH)
    start_sleep_timer()
    cnt = 0
    while True:
        print(f"Main loop tick {cnt}, mode: {MODE}")
        cnt += 1
        if MODE == 0:
            print("Sleeping zzz")
            utime.sleep(4)
            print("Real sleeping")
            utime.sleep(1)
            LED_1.off()
            esp32.wake_on_ext0(pin=BUTTON_DOWNHILL, level=esp32.WAKEUP_ANY_HIGH)
            machine.lightsleep()
            MODE = 5
        elif MODE == 1:
            print(f"Idle")
            LED_1.on()
        elif MODE == 2:
            print("Preparing")
            stop_sleep_timer()
            remove_irq(BUTTON_DATA_TRANSFER)
            remove_irq(BUTTON_DOWNHILL)
            
            LED_1.off()
            blink_timer = Timer(1)
            blink_timer.init(mode=Timer.PERIODIC, period=BLINK_TIME_DERIOD_MS, callback=toggle_led_2)
            CONTROLLER.prepare_run()
            blink_timer.deinit()
            LED_1.on()
        
            add_irq(BUTTON_DATA_TRANSFER, button_transmit_handler)
            add_irq(BUTTON_DOWNHILL, button_downhill_handler)
            start_sleep_timer()
            MODE = 1
        elif MODE == 3:
            print("Running")
            stop_sleep_timer()
            remove_irq(BUTTON_PREPARE_RUN)
            remove_irq(BUTTON_DATA_TRANSFER)
            
            LED_1.off()
            LED_2.on()
            CONTROLLER.main_cycle()
            LED_2.off()
            LED_1.on()
            
            add_irq(BUTTON_PREPARE_RUN, button_prepare_handler)
            add_irq(BUTTON_DATA_TRANSFER, button_transmit_handler)
            start_sleep_timer()
            MODE = 1
        elif MODE == 4:
            print("Transmit data")
            stop_sleep_timer()
            remove_irq(BUTTON_DOWNHILL)
            remove_irq(BUTTON_PREPARE_RUN)
            
            blink_timer = Timer(1)
            blink_timer.init(mode=Timer.PERIODIC, period=BLINK_TIME_DERIOD_MS, callback=toggle_led_1)
            CONTROLLER.transmit_data()
            blink_timer.deinit()
            
            add_irq(BUTTON_DOWNHILL, button_downhill_handler)
            add_irq(BUTTON_PREPARE_RUN, button_prepare_handler)
            start_sleep_timer()
            MODE = 1
        elif MODE == 5: # waking up
            print("Waking up")
            
            blink_timer = Timer(1)
            blink_timer.init(mode=Timer.PERIODIC, period=50, callback=toggle_led_1)
            utime.sleep(5)
            blink_timer.deinit()
        
            start_sleep_timer()
            MODE = 1

        utime.sleep(1)
        
        
        
if __name__ == "__main__":
    Main()


