from machine import Pin, PWM, I2C
from fifo import Fifo
import time
import micropython
from ssd1306 import SSD1306_I2C
micropython.alloc_emergency_exception_buf(200)

## rotary encoder setup


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



timenow = time.ticks_ms()

def button_handler(pin):
    global pressed
    pressed = True
    
rot = RotaryEncoder(10, 11)
rot_button = Pin(12, Pin.IN, Pin.PULL_UP)
rot_button.irq(handler=button_handler, trigger=Pin.IRQ_RISING, hard=True)
rot_button_fifo = Fifo(30, typecode = "i")
pressed = False


led1 = PWM(20, freq=1000)
led2 = PWM(21, freq=1000)
led3 = PWM(22, freq=1000)
test = 0
lasttime = time.ticks_ms()
position = 1

OLED_SDA = 14
OLED_SCL = 15

i2c = I2C(1, scl=Pin(OLED_SCL), sda=Pin(OLED_SDA), freq=400000)
OLED_WIDTH = 128
OLED_HEIGHT = 64
oled = SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2c)
oled.fill(0)

line_height = 15
slot1_ypos = 10
slot2_ypos = slot1_ypos + line_height
slot3_ypos = slot2_ypos + line_height

yposlist = {1: slot1_ypos, 2: slot2_ypos, 3: slot3_ypos}

class Cursor:
    def __init__(self, position):
        self.position = position
        self.graphic = "->"
        self.xpos = 5
        self.ypos = slot1_ypos
    
    def move(self, new_position):
        self.ypos = yposlist[self.position]
        oled.text(self.graphic, self.xpos, self.ypos, 0)
        self.position = new_position
        self.ypos = yposlist[self.position]
        oled.text(self.graphic, self.xpos, self.ypos, 1)
        oled.show()
        print(f"move done - position: {position}, graphic: {self.graphic}, xpos: {self.xpos}, ypos: {self.ypos}")


class Led:
    def __init__(self, pin, position, brightness=300):
        self.pin = PWM(Pin(pin), freq=1000)
        self.brightness = brightness
        self.position = position
        self.state = False
        self.xpos = 70
        
    def toggle(self):
        self.state = not self.state
        print(self.state)
        if self.state:
            oled.text("OFF", self.xpos, yposlist[self.position], 0)
            oled.show()
            oled.text("ON", self.xpos, yposlist[self.position], 1)
            oled.show()    
            self.pin.duty_u16(self.brightness)
        else:
            oled.text("ON", self.xpos, yposlist[self.position], 0)
            oled.show()
            oled.text("OFF", self.xpos, yposlist[self.position], 1)
            oled.show()    
            self.pin.duty_u16(0)        

def drawMenu():
    xpos = 30
    oled.text("LED1:", xpos, yposlist[1], 1)
    oled.text("OFF", 70, yposlist[1], 1)
 
    oled.text("LED2:", xpos, yposlist[2], 1)
    oled.text("OFF", 70, yposlist[2], 1)

    oled.text("LED3:", xpos, yposlist[3], 1)
    oled.text("OFF", 70, yposlist[3], 1)

cursor = Cursor(position)
drawMenu()
cursor.move(1)

led1 = Led(22, 1)
led2 = Led(21, 2)
led3 = Led(20, 3)
    
    
while True:
    
    if pressed:
        pressed = False
        if position == 1:
            led1.toggle()
        if position == 2:
            led2.toggle()
        if position == 3:
            led3.toggle()

    time.sleep(0.1)
    
    if rot.fifo.has_data():
        dir = rot.fifo.get()
        if dir == 1:
            print("direction right")
            if position < 3:
                position += 1
            else:
                position = 3
        if dir == -1:
            print("direction left")
            if position > 1:
                position -= 1
            else:
                position = 1
        cursor.move(position)
        print(position)
        
    