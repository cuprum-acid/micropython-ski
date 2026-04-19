from machine import Pin
import time

led = Pin(2, Pin.OUT, Pin.IN)

def toggle_led():
    print("Toggling LED")
    led.toggle()

# Interrupt handler function
def button_handler(pin):
    # This runs when the interrupt triggers
    print(f"Interrupt on pin {pin}")
    time.sleep(1)
    print("Toggle LED back")
    led.toggle()
    # Note: avoid long operations, delays, or memory allocation inside hard IRQ

led.irq(handler=button_handler, trigger=Pin.IRQ_RISING)


cnt = 0
while True:
    cnt+= 1
    print("Main loop")
    if cnt == 5:
        toggle_led()
    time.sleep(1)