from machine import Pin, PWM
from fifo import Fifo
import time
import micropython
micropython.alloc_emergency_exception_buf(200)

## pin set up

class RotaryEncoder:
    def __init__(self, rot_a, rot_b):
        self.a = Pin(10, mode = Pin.IN, pull = Pin.PULL_UP)
        self.b = Pin(11, mode = Pin.IN, pull = Pin.PULL_UP)
        self.fifo = Fifo(30, typecode = "i")
        self.a.irq(handler = self.handler, trigger = Pin.IRQ_RISING, hard = True)
        
    def handler(self, pin):
        if self.b():
            self.fifo.put(-1)
        else:
            self.fifo.put(1)
            
            
class RotButton:
    def __init__(self, this_pin):
        self.pin = Pin(this_pin, mode = Pin.IN, pull = Pin.PULL_UP)
        self.pin.irq(handler = self.handler, trigger = Pin.IRQ_RISING, hard = True)
        
    def handler(self, pin):
        global state
        state = not state

rot = RotaryEncoder(10, 11)
rot_button = RotButton(12)
state = True

led = PWM(Pin(20), freq=1000)

amount = 800    ## initial brightness
leaps = 10       ## how much the rotary encoder changes amount
limit = 1       ## minimum brightness (values less than zero show up as max)

while True:
    if state:
        if rot.fifo.has_data():
            dir = rot.fifo.get()
            if dir == 1:
                amount += leaps
            if dir == -1:
                if amount > limit:
                    amount -= leaps
                else:
                    amount = limit
        led.duty_u16(amount)
    else:
        led.duty_u16(0)
            
    print("state", state, "brightness", amount)   
    ## print("button value", rot_button.pin.value(), "state", state)
    ## print(rot.a.value(), rot.b.value())
    ## print(amount)
    time.sleep(0.01)