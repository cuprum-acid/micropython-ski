# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()

import network
import time

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

wlan.connect("WIFI", "PASS")

for _ in range(20):
    if wlan.isconnected():
        break
    time.sleep(0.5)

if wlan.isconnected():
    print("Wi-Fi подключен, IP:", wlan.ifconfig())
else:
    print("Не удалось подключиться к Wi-Fi")
