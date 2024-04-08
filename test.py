from machine import Pin 
import time

button = Pin(7, Pin.IN, Pin.PULL_UP)
mode = "text"

while True:
    if button.value():
        print(1)
    else:
        print(2)
    time.sleep(0.5)