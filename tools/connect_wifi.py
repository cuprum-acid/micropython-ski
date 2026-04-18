import network
import time

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

wlan.connect("YY_Alisa", "88888888!")

for _ in range(20):
    if wlan.isconnected():
        break
    time.sleep(0.5)

if wlan.isconnected():
    print("Wi-Fi подключен, IP:", wlan.ifconfig()[0])
else:
    print("Не удалось подключиться к Wi-Fi")